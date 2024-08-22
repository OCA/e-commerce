.. image:: https://pbs.twimg.com/profile_images/547133733149483008/0JKHr3Av_400x400.png
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

Website Sale Cart Quantity Shop
=======================================

- **Plus and Minus Buttons**: 
  - Users can increase or decrease the quantity of a product by clicking the plus (+) or minus (−) buttons next to the quantity input field.
  - Clicking the plus button increments the quantity by 1.
  - Clicking the minus button decrements the quantity by 1, with a minimum value of 0.

- **Direct Input**: 
  - Users can manually enter the desired quantity directly into the input box in the middle of the buttons.
  - The input field validates and updates the quantity based on user input.

- **Dynamic Updates**:
  - The quantity input field dynamically updates the cart when the quantity is changed using either the buttons or by direct input.
  - The system ensures that the quantity displayed is in sync with the quantity available in the cart.

- **Visual Feedback**:
  - The input field's background color and text color change when the quantity matches the available stock, providing visual feedback to the user.

Usage
=====

1. **Navigate to the Shop Page**:
   - Go to your shop or category page in the Odoo eCommerce interface.

2. **Adjust Product Quantity**:
   - Use the plus (+) button to increase the quantity by 1.
   - Use the minus (−) button to decrease the quantity by 1, ensuring the quantity does not drop below 0.
   - Enter a specific quantity directly into the input field to set the desired amount.

3. **Visual Feedback**:
   - Observe changes in the input field color to reflect the available stock.

Configuration
=============

No additional configuration is required. The module integrates seamlessly with the existing product quantity functionality on the shop page.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/avanzosc/odoo-addons/issues>`_. If you encounter any issues, please check there to see if your issue has already been reported. If not, provide detailed feedback to help us resolve it.

Credits
=======

Contributors
------------
* Unai Beristain <unaiberistain@avanzosc.es>

Do not contact contributors directly about support or help with technical issues.

License
=======
This project is licensed under the AGPL-3 License. For more details, please refer to the LICENSE file or visit <http://www.gnu.org/licenses/agpl-3.0-standalone.html>.
