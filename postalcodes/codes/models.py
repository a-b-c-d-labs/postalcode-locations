from django.db import models


class Country(models.Model):
    name = models.CharField(max_length=150, blank=False, null=True)
    country_code = models.CharField(max_length=4, blank=True, null=True)
    created = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    last_status_change = models.DateTimeField(default=datetime.now, blank=True, editable=True)
    active = models.CharField(max_length=10, blank=False, null=True)


class State(models.Model):
    name = models.CharField(max_length=150, blank=False, null=True)
    abv_name = models.CharField(max_length=150, blank=False, null=True)
    country = models.ForeignKey(Country, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    active = models.CharField(max_length=10, blank=False, null=True, default='active')
    created = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    last_status_change = models.DateTimeField(default=datetime.now, blank=True, editable=True)


class City(models.Model):
    name = models.CharField(max_length=150, blank=False, null=True)
    state = models.ForeignKey(State, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    active = models.CharField(max_length=10, blank=False, null=True, default='active')
    created = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    last_status_change = models.DateTimeField(default=datetime.now, blank=True, editable=True)


class PostalCode(models.Model):
    name = models.CharField(max_length=150, blank=False, null=True)
    active = models.CharField(max_length=10, blank=False, null=True, default='active')
    created = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    last_status_change = models.DateTimeField(default=datetime.now, blank=True, editable=True)


class Asent(models.Model):
    name = models.CharField(max_length=150, blank=False, null=True)
    kind = models.CharField(max_length=150, blank=False, null=True)
    zone = models.CharField(max_length=150, blank=False, null=True)
    city = models.ForeignKey(City, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    postal_code = models.ForeignKey(PostalCode, related_name='+', null=True, blank=True, on_delete=models.SET_NULL)
    active = models.CharField(max_length=10, blank=False, null=True, default='active')
    created = models.DateTimeField(default=datetime.now, blank=True, editable=False)
    last_status_change = models.DateTimeField(default=datetime.now, blank=True, editable=True)


class AddressManager(models.Manager):
    def as_data(self, address):
        data = model_to_dict(address, exclude=['id', 'user'])
        if isinstance(data['country'], Country):
            data['country'] = data['country'].code
        return data

    def are_identical(self, addr1, addr2):
        data1 = self.as_data(addr1)
        data2 = self.as_data(addr2)
        return data1 == data2

    def store_address(self, user, address):
        data = self.as_data(address)
        address, dummy_created = user.addresses.get_or_create(**data)
        return address


class PossiblePhoneNumberField(PhoneNumberField):
    """Less strict field for phone numbers written to database."""
    default_validators = [validate_possible_number]


class Address(models.Model):
    first_name = models.CharField(max_length=256, blank=True)
    last_name = models.CharField(max_length=256, blank=True)
    company_name = models.CharField(max_length=256, blank=True)
    internal_number = models.CharField(max_length=30, blank=True)
    external_number = models.CharField(max_length=30, blank=True)
    floor = models.CharField(max_length=30, blank=True)
    street_address_1 = models.CharField(max_length=256, blank=True)
    street_address_2 = models.CharField(max_length=256, blank=True)
    city = models.ForeignKey(City, null=True, blank=True, on_delete=models.SET_NULL)
    city_area = models.CharField(max_length=200, blank=True)
    postal_code = models.ForeignKey(PostalCode, null=True, blank=True, on_delete=models.SET_NULL)
    country = models.ForeignKey(Country, null=True, blank=True, on_delete=models.SET_NULL)
    country_area = models.CharField(max_length=150, blank=True)
    state = models.ForeignKey(State, null=True, blank=True, on_delete=models.SET_NULL)
    colony = models.ForeignKey(Asent, null=True, blank=True, on_delete=models.SET_NULL)
    phone = models.CharField(max_length=30, blank=True, default='')
    anotations = models.TextField(null=True, blank=True, default='')
    objects = AddressManager()

    @property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)

    class Meta:
        verbose_name = pgettext_lazy('Address model', 'address')
        verbose_name_plural = pgettext_lazy('Address model', 'addresses')

    def __str__(self):
        if self.company_name:
            return '{0} - {1}'.format(self.company_name, self.full_name)
        return self.full_name

    def __repr__(self):
        return ('Address(first_name={0}, last_name={1}, company_name={2},'
                'street_address_1={3}, street_address_2={4}, city_id={5},'
                'postal_code_id={6}, country_id={7}, country_area={8}, phone={9})'
                .format(self.first_name, self.last_name, self.company_name,
                self.street_address_1, self.street_address_2, self.city_id,
                self.postal_code_id, self.country_id, self.country_area,
                self.phone))
