1. Go to *Inventory / Configuration / Attributes* (or
   *Sales / Configuration / Attributes*).
2. Open the attribute you want to use as a range filter (e.g., "SCA Score",
   "Weight", "Volume").
3. Set the **Display Type** to **Range Slider**.
4. The **Variant Creation** will be automatically set to "Never" since range
   sliders are not compatible with variant generation.
5. Set the **Range Step** value (default 0.5). Use 1 for integer steps.
6. For each attribute value, ensure the **Numeric Value** field is set. The
   module will attempt to parse it from the value name automatically, but
   you can also set it manually.
7. Make sure the attribute **Visibility** is set to "Visible".
