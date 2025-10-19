psa-global-insights/
│
├── 📄✅ main.py                              # Application entry point
├── 📄✅ requirements.txt                     # Python dependencies
├── 📄✅ README.md                            # Project documentation
├── 📄 .gitignore                           # Git ignore rules
├── 📄 .env.example                         # Environment variables template
│
├── 📁 frontend/                            # FRONTEND LAYER
│   ├── 📄 __init__.py
│   ├── 📄 config.py                        # UI/UX configuration (colors, metrics, charts)
│   │
│   ├── 📁 components/                      # Reusable UI components
│   │   ├── 📄 __init__.py
│   │   ├── 📄 sidebar.py                   # Navigation sidebar with filters
│   │   ├── 📄 header.py                    # Page header component
│   │   ├── 📄 chat_interface.py            # AI chat component
│   │   ├── 📄 kpi_cards.py                 # Metric cards component
│   │   └── 📄 alerts.py                    # Alert notifications component
│   │
│   └── 📁 pages/                           # Dashboard pages
│       ├── 📄 __init__.py
│       ├── 📄✅ global_insights.py           # Main overview dashboard
│       ├── 📄 vessel_performance.py        # Vessel analytics page
│       ├── 📄 sustainability.py            # Carbon tracking page
│       └── 📄 berth_management.py          # Berth operations page
│
├── 📁 backend/                             # BACKEND LAYER
│   ├── 📄 __init__.py
│   ├── 📄✅ ai_service.py                    # Multi-model Azure OpenAI service
│   ├── 📄✅ query_handler.py                 # Smart query router
│   ├── 📄 insights_generator.py            # Proactive insights engine
│   ├── 📄 context_manager.py               # Conversation state management
│   └── 📄 sql_generator.py                 # Natural language to SQL converter
│
├── 📁 data/                                # DATA LAYER
│   ├── 📄 __init__.py
│   ├── 📄✅ database_manager.py              # MySQL database operations
│   ├── 📄✅ api_integrations.py              # MarineTraffic & OpenWeather APIs
│   ├── 📄 etl_pipeline.py                  # ETL and data synchronization
│   ├── 📄 schema.sql                       # Complete database schema
│   ├── 📄 seed_data.sql                    # Sample data for testing
│   └── 📄 vector_store.py                  # Embeddings storage and retrieval
│
├── 📁 visualizations/                      # VISUALIZATION LAYER
│   ├── 📄 __init__.py
│   ├── 📄✅ charts.py                        # Advanced Plotly chart library
│   ├── 📄 maps.py                          # Geographic visualizations
│   ├── 📄 dashboards.py                    # Pre-built dashboard layouts
│   └── 📄 themes.py                        # Chart themes and styling
│
├── 📁 config/                              # CONFIGURATION
│   ├── 📄 __init__.py
│   ├── 📄 settings.py                      # Application settings
│   ├── 📄 .env.example                     # Environment variables template
│   └── 📄 logging.conf                     # Logging configuration
│
├── 📁 utils/                               # UTILITIES
│   ├── 📄 __init__.py
│   ├── 📄 helpers.py                       # Helper functions
│   ├── 📄 validators.py                    # Data validation
│   ├── 📄 formatters.py                    # Data formatting utilities
│   └── 📄 constants.py                     # Application constants
│
├── 📁 tests/                               # TESTING
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                      # Pytest configuration
│   ├── 📄 test_ai_service.py               # AI service tests
│   ├── 📄 test_database.py                 # Database tests
│   ├── 📄 test_api_integrations.py         # API tests
│   ├── 📄 test_visualizations.py           # Visualization tests
│   └── 📄 test_query_handler.py            # Query handler tests
│
├── 📁 scripts/                             # AUTOMATION SCRIPTS
│   ├── 📄 setup_database.sh                # Database initialization script
│   ├── 📄 scheduled_sync.py                # Cron job for data sync
│   ├── 📄 generate_reports.py              # Automated report generation
│   └── 📄 backup_database.sh               # Database backup script
│
├── 📁 docs/                                # DOCUMENTATION
│   ├── 📄 architecture.md                  # Architecture overview
│   ├── 📄 api_reference.md                 # API documentation
│   ├── 📄 deployment.md                    # Deployment guide
│   ├── 📄 user_guide.md                    # User manual
│   └── 📁 images/                          # Documentation images
│       ├── architecture_diagram.png
│       ├── screenshot_dashboard.png
│       └── flow_diagram.png
│
├── 📁 assets/                              # STATIC ASSETS
│   ├── 📁 images/
│   │   ├── logo.png
│   │   ├── favicon.ico
│   │   └── placeholder.svg
│   ├── 📁 icons/
│   │   ├── vessel.svg
│   │   ├── port.svg
│   │   └── carbon.svg
│   └── 📁 css/
│       └── custom_styles.css
│
├── 📁 docker/                              # DOCKER CONFIGURATION
│   ├── 📄 Dockerfile                       # Main Dockerfile
│   ├── 📄 docker-compose.yml               # Docker Compose configuration
│   ├── 📄 .dockerignore                    # Docker ignore rules
│   └── 📁 nginx/
│       └── 📄 nginx.conf                   # Nginx configuration
│
└── 📁 .github/                             # GITHUB ACTIONS (Optional)
    └── 📁 workflows/
        ├── 📄 tests.yml                    # CI/CD testing workflow
        ├── 📄 deploy.yml                   # Deployment workflow
        └── 📄 code_quality.yml             # Linting and quality checks