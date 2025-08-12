# KSSEM College Virtual AI Assistant

A comprehensive kiosk-based Virtual AI Assistant system designed specifically for KSSEM College, providing seamless campus navigation, query resolution, and resource access through an intelligent multimodal interface.

## Features

- **Smart Campus Navigation**: Real-time SLAM-based mapping and route optimization
- **Multimodal Interface**: Voice, text, and touch interactions for accessibility
- **AI-Powered Query Resolution**: BERT-based natural language processing
- **Resource Integration**: Secure access to college systems (Moodle, library, events)
- **Privacy-First Design**: GDPR-compliant data handling with encryption

## System Architecture

The system follows a 4-layer architecture:
1. **Presentation Layer**: Touchscreen GUI, voice interface, and accessibility features
2. **Application Layer**: Query processing, navigation, and resource access modules
3. **AI Processing Layer**: Cloud-hosted NLP and SLAM engines
4. **Data Layer**: Secure storage and API integration

## Technology Stack

- **NLP**: BERT/DistilBERT for query understanding
- **SLAM**: ORB-SLAM3 for campus mapping
- **Cloud**: AWS for scalable infrastructure
- **Security**: AES-256 encryption and GDPR compliance
- **UI**: Python Tkinter for responsive touchscreen interface

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Configure KSSEM-specific settings in `config/kssem_config.py`
3. Run the main application: `python src/main.py`

## KSSEM Personalization

This system is specifically configured for KSSEM College with:
- Custom campus map and building layouts
- College-specific resource databases
- Localized content and multilingual support
- Integration with KSSEM's existing systems

## License

MIT License - See LICENSE file for details