# app.py
# Unit converter Gradio app for Hugging Face Spaces
# Works with Gradio Blocks

import gradio as gr
from typing import Union

# -----------------------
# Conversion data
# -----------------------
CONVERSIONS = {
    "Length": {
        "base": "m",
        "units": {"m":1, "km":1000, "cm":0.01, "mm":0.001, "mi":1609.344, "yd":0.9144, "ft":0.3048, "in":0.0254}
    },
    "Mass": {
        "base": "kg",
        "units": {"kg":1, "g":0.001, "mg":1e-6, "lb":0.45359237, "oz":0.0283495}
    },
    "Temperature": {"units": ["°C", "°F", "K"]},
    "Time": {
        "base": "s",
        "units": {"s":1, "min":60, "h":3600, "day":86400}
    },
    "Speed": {
        "base": "m/s",
        "units": {"m/s":1, "km/h":1000/3600, "mph":1609.344/3600, "knot":1852/3600}
    },
    "Area": {
        "base": "m²",
        "units": {"m²":1, "cm²":0.0001, "mm²":1e-6, "km²":1e6, "ft²":0.092903, "in²":0.00064516, "acre":4046.856, "hectare":10000}
    },
    "Volume": {
        "base": "L",
        "units": {"L":1, "mL":0.001, "m³":1000, "cm³":0.001, "ft³":28.3168, "in³":0.0163871, "gal(US)":3.78541, "qt(US)":0.946353}
    },
    "Energy": {
        "base": "J",
        "units": {"J":1, "kJ":1000, "Wh":3600, "kWh":3.6e6, "cal":4.184, "kcal":4184}
    },
    "Pressure": {
        "base": "Pa",
        "units": {"Pa":1, "kPa":1000, "bar":1e5, "atm":101325, "psi":6894.76, "mmHg":133.322}
    },
    "Data": {
        "base": "byte",
        "units": {"bit":1/8, "byte":1, "KB":1024, "MB":1024**2, "GB":1024**3, "TB":1024**4}
    },
    "Angle": {
        "base": "rad",
        "units": {"deg":3.141592653589793/180, "rad":1, "grad":3.141592653589793/200}
    }
}

def get_units(category: str):
    if category == "Temperature":
        return CONVERSIONS["Temperature"]["units"]
    return list(CONVERSIONS[category]["units"].keys())

def convert(category: str, value: Union[int, float], from_unit: str, to_unit: str) -> str:
    try:
        if value is None:
            return "❌ Enter a number."
        if from_unit == to_unit:
            return f"{value} {from_unit} = {value} {to_unit}"
        if category == "Temperature":
            # normalize to Celsius as base
            if from_unit == "°C":
                base = float(value)
            elif from_unit == "°F":
                base = (float(value) - 32) * 5.0 / 9.0
            elif from_unit == "K":
                base = float(value) - 273.15
            else:
                return "❌ Invalid temperature unit."
            if to_unit == "°C":
                result = base
            elif to_unit == "°F":
                result = base * 9.0/5.0 + 32
            elif to_unit == "K":
                result = base + 273.15
            else:
                return "❌ Invalid temperature unit."
        else:
            units = CONVERSIONS[category]["units"]
            base_val = float(value) * units[from_unit]    # to base
            result = base_val / units[to_unit]
        # Nice formatting
        if abs(result - round(result)) < 1e-9:
            out = f"{int(round(result))}"
        else:
            out = f"{round(result, 6):.6f}".rstrip('0').rstrip('.')
        return f"{value} {from_unit} = {out} {to_unit}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

# -----------------------
# Gradio UI
# -----------------------
history = []

with gr.Blocks(css=".gradio-container {max-width:900px}") as demo:
    gr.Markdown("## 🌍 Unit Converter — Gradio (Hugging Face Spaces)\nChoose a category, units, enter a value, and press Convert.")

    with gr.Row():
        category = gr.Dropdown(choices=list(CONVERSIONS.keys()), label="Category", value="Length")

    # set default units for Length
    default_units = get_units("Length")

    with gr.Row():
        from_unit = gr.Dropdown(choices=default_units, value=default_units[0], label="From Unit")
        to_unit = gr.Dropdown(choices=default_units, value=default_units[1], label="To Unit")

    with gr.Row():
        value_in = gr.Number(label="Value", value=1)

    convert_btn = gr.Button("Convert")
    output = gr.Textbox(label="Result")
    hist_box = gr.Textbox(label="History (last 10)", interactive=False)

    # Update units when category changes
    def update_units(cat):
        units = get_units(cat)
        f = units[0] if units else None
        t = units[1] if len(units) > 1 else units[0] if units else None
        return gr.update(choices=units, value=f), gr.update(choices=units, value=t)

    def do_convert(cat, val, f, t):
        res = convert(cat, val, f, t)
        history.append(res)
        if len(history) > 100:
            history.pop(0)
        hist_txt = "\n".join(history[-10:])
        return res, hist_txt

    category.change(fn=update_units, inputs=category, outputs=[from_unit, to_unit])
    convert_btn.click(fn=do_convert, inputs=[category, value_in, from_unit, to_unit], outputs=[output, hist_box])

if __name__ == "__main__":
    demo.launch()
