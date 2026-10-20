//! Streaming prediction with the existing frozen Rust coefficients. NO fitting.
use serde_json::{json, Value};
use std::{env, fs, io::{self, BufRead}};

fn predict(request: &Value, models: &Value) -> Result<Value, String> {
    let long = request["long_side"].as_f64().ok_or("missing long side")?;
    let short = request["short_side"].as_f64().ok_or("missing short side")?;
    if !long.is_finite() || !short.is_finite() || long <= 0. || short <= 0. {
        return Err("invalid box".into());
    }
    let script = request["script"].as_str().ok_or("missing script")?;
    let group = if models.get(script).is_some() { script } else { "pooled" };
    let model = &models[group][2];
    let b = model["coefficients"].as_array().ok_or("missing frozen coefficients")?;
    if b.len() != 3 { return Err("invalid coefficients".into()); }
    let x = [1., (long / short).ln(), 0.];
    // Same operation/order/clamp as font_calibration.rs::prediction(mode=2).
    let expected = ((0..3).map(|i| x[i] * b[i].as_f64().unwrap()).sum::<f64>()).clamp(0., 12.).exp() - 1.;
    Ok(json!({"expected":expected, "group":group, "script_specific":group!="pooled"}))
}
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let path = env::args().nth(1).ok_or("usage: greekocr-frozen-font-predict MODELS.json")?;
    let frozen: Value = serde_json::from_slice(&fs::read(path)?)?;
    for line in io::stdin().lock().lines() {
        let answer = match line {
            Ok(raw) => match serde_json::from_str::<Value>(&raw) {
                Ok(request) => match predict(&request, &frozen["models"]) {
                    Ok(result) => json!({"ok":true,"result":result}),
                    Err(error) => json!({"ok":false,"error":error})
                },
                Err(error) => json!({"ok":false,"error":error.to_string()})
            },
            Err(error) => json!({"ok":false,"error":error.to_string()})
        };
        println!("{}", answer);
    }
    Ok(())
}
