# Data mining module

    # "onecall" gets current, forecast and historical weather data
    # https://openweathermap.org/api/one-call-api

     # https://developer.tibber.com/docs/reference#home
      # home.info :
      # {'viewer': {'home': {
      #   'appNickname': 'Home Up',
      #   'features': {
      #     'realTimeConsumptionEnabled': True
      #     },
      #   'currentSubscription': {
      #     'status': 'running',
      #     'priceInfo': {
      #       'current': {
      #         'currency': 'NOK'
      #         }
      #       }
      #     },
      #   'address': {
      #     'address1': 'Per Sivles veg 11c',
      #     'address2': None,
      #     'address3': None,
      #     'city': 'TRONDHEIM',
      #     'postalCode': '7071',
      #     'country': 'NO',
      #     'latitude': '63.4000176',
      #     'longitude': '10.3353076'},
      #   'meteringPointData': {
      #     'consumptionEan': '707057500067891635',
      #     'energyTaxType': 'none',
      #     'estimatedAnnualConsumption': 6195,
      #     'gridCompany': 'Tensio TS AS',
      #     'productionEan': None,
      #     'vatType': 'normal'},
      #   'owner': {
      #     'name': 'Sebastien Nicolas Gros',
      #     'isCompany': None,
      #     'language': 'en-US',
      #     'contactInfo': {
      #       'email': 'sebastien.gros@ntnu.no',
      #       'mobile': '+4745917969'
      #       }
      #     },
      #   'timeZone': 'Europe/Oslo',
      #   'subscriptions': [{
      #     'id': 'b0062466-9477-478e-8173-4bd9da06b375',
      #     'status': 'running',
      #     'validFrom': '2020-12-25T23:00:00+00:00',
      #     'validTo': None,
      #     'statusReason': None
      #     }]
      # }}}

      # Sensibo
    ## measurement
    # {'time': {'secondsAgo': 50, 'time': '2021-02-15T12:09:36.571151Z'},
    #  'temperature': 19.5,
    #  'humidity': 45.6}
    ## state
    # {'on': True,
    #  'fanLevel': 'medium_high',
    #  'timestamp': {'secondsAgo': 0, 'time': '2021-02-15T12:11:07.722080Z'},
    #  'temperatureUnit': 'C',
    #  'horizontalSwing': 'fixedCenter',
    #  'targetTemperature': 20,
    #  'mode': 'heat',
    #  'swing': 'fixedMiddleTop'}