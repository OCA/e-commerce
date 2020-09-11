#. Go to shop
#. Drop down 'Customize' menu
#. Enable 'Price Filter' option

Theming
~~~~~~~

CSS Classes:

- ``js_attribute_filter_price`` > The class-trigger to initialize the slider
- ``price_filter_main`` > The main container (slider + inputs + button)

HTML ID's:

- ``filter_price_slider`` > The Slider
- ``price_range_min_value`` > The input for minimum price
- ``price_range_max_value`` > The input for maximum price
- ``price_slider_form`` > The submit button

HTML Attributes:

``filter_price_slider`` accepts the following attributes:

    - ``data-custom_min_price`` > Float > Used to store the user min. value
    - ``data-custom_max_price`` > Float > Used to store the user max. value
    - ``data-max_price`` > Float > Used in the slider configuration to set the max. value
    - ``data-symbol`` > Char > Used in the slider configuration to set the currency symbol
    - ``data-options`` > Dict > You can use this to overwrite all slider configuration values
