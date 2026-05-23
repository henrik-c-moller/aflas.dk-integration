# Aflas.dk Water Meter for Home Assistant

# Aflas.dk Water Meter for Home Assistant

![HACS Custom](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)
![Version](https://img.shields.io/github/v/release/henrikmoller/aflas_dk?label=version)
![Downloads](https://img.shields.io/github/downloads/henrikmoller/aflas_dk/total.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)

This custom integration provides access to water consumption data from **Aflas.dk** directly inside Home Assistant.  
It exposes a sensor that reports **today’s realtime water usage in cubic meters (m³)**, updated throughout the day, and fully compatible with the **Home Assistant Energy Dashboard**.

The integration is configured entirely through the **Home Assistant UI (config flow)** — no YAML required.

---

## 🚀 Installation (HACS)

1. Open **HACS → Integrations**
2. Select **Custom repositories**
3. Add your GitHub repository  
   - Category: **Integration**
4. Install the integration from HACS
5. Restart Home Assistant

---

## ⚙️ Setup via UI (Config Flow)

After installation:

1. Go to **Settings → Devices & Services**
2. Click **Add Integration**
3. Search for **Aflas.dk**
4. Enter:
   - **Username**
   - **Password**
   - **Værknummer** (utility ID)

The integration will **validate your login** before creating the configuration entry.  
If the credentials are incorrect, Home Assistant will show an error message.

---

## 🛠️ Changing Login Details (Options Flow)

You can update your credentials without removing the integration:

1. Go to **Settings → Devices & Services**
2. Locate **Aflas.dk**
3. Click **Configure**
4. Update:
   - Username  
   - Password  
   - Værknummer  

The integration validates the login again before saving changes.

---

## 📊 Sensor Information

The integration exposes one primary sensor:

### **Aflas.dk Water Usage (m³)**  
- Shows **today’s realtime consumption**
- Increases throughout the day
- Automatically resets at midnight (based on Aflas.dk data)
- Fully compatible with **Energy Dashboard**
- Uses date‑matching logic to correctly identify today’s usage from Aflas.dk’s label/usage arrays

---

## 🔄 Update Interval

Data is refreshed automatically every **hour**

---

## 📝 Notes

This integration is **not affiliated with Aflas.dk**.  
It is provided for personal use and without warranty.

---


