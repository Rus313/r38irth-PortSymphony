# 🚢 Reberth AI

**A Conversational Assistant for Global Coordination in Port Operations**

*Theme: Network Insights – Conversational AI for Global Coordination*

---

## 🧭 Overview

TradeLink AI is a conversational AI assistant designed to help PSA and port operators gain real-time visibility and insights into vessel schedules, port congestion, and global disruptions. Through natural language queries, users can coordinate port operations efficiently — keeping trade moving in the face of uncertainty.

## 🎯 Problem Statement

Global port operations face increasing challenges from:

- **Off-schedule vessel arrivals & congestion**
- **Fragmented systems with poor coordination**
- **Rising disruptions due to climate and geopolitical instability**

These issues lead to inefficiencies, delays, and underutilized resources.

## 🌐 Our Solution

TradeLink AI enables port and supply chain stakeholders to:

- **Ask questions like:**
  - "Which vessels are delayed today at Tuas?"
  - "Show congestion hotspots in Southeast Asia."
  - "Predict berthing delays for the next 12 hours."
- **Get instant responses** powered by LLMs and real-time data
- **Visualize global port congestion**, ETAs, and disruptions on a live dashboard

## 👥 Target Users

- PSA Port Managers
- Terminal Operators & Vessel Traffic Controllers
- Global Logistics & Supply Chain Planners

## 🔧 Key Features

### 🤖 Conversational AI
- Natural language interface powered by OpenAI's GPT model
- Supports both predefined and open-ended queries

### 📡 Real-Time Vessel Insights
- Live vessel schedules and ETAs from integrated APIs (e.g., MPA, MarineTraffic)
- Delay and queue prediction using historical and current data

### 🌍 Port Congestion Visualization
- Interactive map showing traffic and congestion across global ports
- Alert system for delay-prone routes or high-load berths

### ⚠️ Disruption Detection
- Weather and routing data to identify and flag disruptions (e.g., Red Sea detours, typhoons)
- Risk scoring for vessel arrival bunching and port delays

### 🌱 (Optional) Sustainability Mode
- Suggest lower-emission routes and port alternatives
- Track CO₂ reduction potential via scheduling optimization

## 🧱 Tech Stack

| Layer | Tools Used |
|-------|------------|
| **Frontend** | Streamlit / Flask, Plotly, Leaflet |
| **Backend** | Python, OpenAI GPT API, LangChain |
| **Data Sources** | MPA Vessel API, OpenWeatherMap, Simulated Port Data |
| **Visualization** | Plotly, Mapbox, Streamlit Components |
| **Hosting** | AWS / Heroku / Local Server |

## 🗓 Hackathon Timeline

| Milestone | Goal |
|-----------|------|
| ✅ **Day 1 AM** | Define problem, choose APIs |
| 🔄 **Day 1 PM** | Build chat interface + sample queries |
| 🔧 **Day 2 AM** | Integrate APIs, develop basic prediction |
| 🎯 **Day 2 PM** | Visualizations + live demo prep |

## 📈 Success Metrics

- **<2 second** response time to most queries
- **80%+** prediction accuracy for vessel delay alerts
- **Usable MVP** by end of hackathon with real-time data and demo scenario

## ⚠️ Known Limitations

- May rely on simulated or limited-scope APIs due to data access restrictions
- MVP focuses on Singapore and Southeast Asia; global expansion is planned
- Sustainability features are stretch goals for post-hackathon development

## 📦 Setup Instructions

### Prerequisites
- Python 3.8+
- OpenAI API Key
- MPA API Access (optional)

### Installation

```bash
# Clone the repository
git clone https://github.com/your-repo/tradelink-ai.git
cd tradelink-ai

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env file with your API keys

# Run the application
streamlit run app.py
```

### Environment Variables

Create a `.env` file with the following:

```env
OPENAI_API_KEY=your_openai_key_here
MPA_API_KEY=your_mpa_key_here
WEATHER_API_KEY=your_weather_key_here
```

## 📚 Data Sources

- [MPA Singapore Vessel Arrivals API](https://www.mpa.gov.sg)
- [OpenWeatherMap API](https://openweathermap.org/api)
- [Data.gov.sg – Vessel Arrivals (Historical)](https://data.gov.sg)
- [MarineTraffic](https://www.marinetraffic.com) (Optional/Trial)

## 🚀 Demo Scenarios

> **Scenario 1: Storm Disruption Management**
> 
> "A storm in the Indian Ocean has rerouted three vessels. One of them is expected to arrive at Tuas Port during peak hour tomorrow. TradeLink AI identifies the risk of berth delay and suggests an alternate slot, reducing waiting time by 3 hours."

## 🤝 Team & Acknowledgements

Built for **PSA Hackathon 2025** under **Theme 2: Network Insights**. 

Special thanks to:
- PSA mentors
- The open data community

## 📝 License

[Insert License Type Here]

## 📧 Contact

[Your contact information or team details]

---

*Last updated: [Date]*
