
# Babua-bihari - Bihar Tourism Expert Chatbot
### {Bihar ke baani; vastavvikta mein jiyelaa}


[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-copyrights_reserved-red)](LICENSE)

An AI-powered chatbot specializing in Bihar tourism and culture, featuring a charismatic Bihari personality with real-time web search capabilities.

![Chat Interface Demo](https://raw.githubusercontent.com/SURYANSH-RAI/Babua-bihari/main/screenshots/Babua-bihari.png) <!-- Add actual screenshot later -->

## Features ✨

- **Cultural Persona**: Sharp-tongued Bihari personality with local slang and humor
- **Real-Time Knowledge**: Integrated Tavily search API for fresh information
- **Conversational Memory**: Maintains context for 3 previous interactions
- **Multimedia Responses**: Images and source citations for rich answers
- **Streaming Interface**: Real-time typed response experience
- **Domain-Focused**: Curated list of trusted Bihar information sources

## Installation 🛠️

1. **Clone Repository**
```bash
git clone https://github.com/SURYANSH-RAI/Babua-bihari.git
cd Babua-bihari
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Environment Setup**
```bash
cp .env.example .env
# Add your API keys to .env
```

## Configuration ⚙️

Create `.env` file with:
```ini
TAVILY_API_KEY=your_tavily_key
GOOGLE_API_KEY=your_gemini_key
```

## Tech Stack 🔧

**Backend**
- Flask (Python web framework)
- Google Generative AI (Gemini 2.0 Flash)
- LangChain (Prompt templating)
- Tavily (Real-time web search)

**Frontend**
- Vanilla JavaScript (EventSource API)
- Modern CSS (Grid/Flexbox layouts)
- HTML5 (Semantic markup)

## API References 🔗

- [Google Generative AI](https://ai.google.dev/)
- [Tavily Search API](https://tavily.com/)
- [LangChain Framework](https://python.langchain.com/)

## Usage 💬

1. Start the Flask server
```bash
python app.py
```

2. Open `http://localhost:5000` in browser

3. Try queries like:
```
- Batawa hoo, humaar Nalanda Vishwavidhyalay ke itihas?
- Patna se Bhopal khattir sabse neek aur sasta train kaun-kaun ba?
- Bihar ke famous litti-chokha kehar mili?
```

## Contributing 🤝

1. Fork the repository
2. Create feature branch
3. Submit PR with detailed description

## License 📄

Copyright License - See [LICENSE](LICENSE) for details

## Acknowledgments 🙏

- Google Gemini for conversational AI capabilities
- Tavily for real-time web search
- Inspired by the rich cultural heritage of Bihar

```
**Note**: This project uses AI-generated content. Verify critical information from official sources.
```
