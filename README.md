# Company Sync - Frappe Application

## Overview

Company Sync is a Frappe application designed to synchronize data between different systems, with a focus on VTiger CRM integration. It provides a robust and flexible framework for managing data consistency across platforms, ensuring seamless operation and data accuracy.

## Key Features

-   **Bidirectional Data Sync:** Enables synchronization of data in both directions between VTiger CRM and Frappe, ensuring that records are consistent across both systems.
-   **Real-time Progress Tracking:** Offers real-time monitoring of the synchronization process, providing insights into the status and progress of data transfer.
-   **Custom Field Mapping:** Supports custom field mappings, allowing users to define how fields in VTiger CRM correspond to fields in Frappe.
-   **Comprehensive Error Logging:** Captures and logs errors during the synchronization process, facilitating quick identification and resolution of issues.
-   **Transaction Management:** Implements transaction management to ensure data integrity during synchronization, preventing partial updates and data corruption.
-   **Entity Relationship Handling:** Manages relationships between different entities, ensuring that related records are synchronized correctly.
-   **Customizable and Extensible:** Designed with customization in mind, allowing developers to extend the application to support additional entities and synchronization scenarios.

## Architecture

The application is structured into several key components:

-   **Sync Engine:** Manages the overall synchronization process, coordinating data transfer and transformation between systems.
-   **Data Processors:** Handle the transformation of data for specific entity types, ensuring that data is correctly formatted and mapped between systems.
-   **Database Handlers:** Manage database connections and transactions, providing a consistent interface for data access.
-   **Progress Observers:** Track and report the progress of the synchronization process, providing real-time feedback to users.
-   **Configuration Management:** Provides a centralized configuration system for managing application settings and mappings.

### Directory Structure

```
company_sync/
├── company_sync/
│   ├── __init__.py
│   ├── dashboard_chart/
│   │   └── sync_error_logs/
│   │       ├── sync_error_logs.json
│   ├── dashboard_chart_source/
│   │   ├── __init__.py
│   │   └── company_sync_data/
│   │       ├── __init__.py
│   │       ├── company_sync_data.js
│   │       ├── company_sync_data.json
│   │       └── company_sync_data.py
│   ├── doctype/
│   │   ├── __init__.py
│   │   ├── company_sync_log/
│   │   │   ├── __init__.py
│   │   │   ├── company_sync_log.js
│   │   │   ├── company_sync_log.json
│   │   │   ├── company_sync_log.py
│   │   │   └── test_company_sync_log.py
│   │   ├── company_sync_scheduler/
│   │   │   ├── __init__.py
│   │   │   ├── company_sync_scheduler_list.js
│   │   │   ├── company_sync_scheduler.css
│   │   │   ├── company_sync_scheduler.js
│   │   │   ├── company_sync_scheduler.json
│   │   │   ├── company_sync_scheduler.py
│   │   │   ├── test_company_sync_scheduler.py
│   │   │   ├── config/
│   │   │   │   ├── config.py
│   │   │   │   ├── logging.py
│   │   │   │   └── mapping/
│   │   │   │       ├── handler.json
│   │   │   │       └── salesorder.json
│   │   │   ├── database/
│   │   │   │   ├── base.py
│   │   │   │   ├── client.py
│   │   │   │   ├── engine.py
│   │   │   │   └── unit_of_work.py
│   │   │   ├── models/
│   │   │   │   └── vtigercrm_salesordercf.py
│   │   │   ├── syncer/
│   │   │   │   ├── syncer.py
│   │   │   │   ├── utils.py
│   │   │   │   ├── handlers/
│   │   │   │   │   ├── crm_handler.py
│   │   │   │   │   ├── csv_handler.py
│   │   │   │   │   └── so_updater.py
│   │   │   │   ├── observer/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── base.py
│   │   │   │   │   └── frappe.py
│   │   │   │   ├── processors/
│   │   │   │   │   └── csv_processor.py
│   │   │   │   ├── repositories/
│   │   │   │   │   └── crm_repository.py
│   │   │   │   ├── services/
│   │   │   │   │   ├── query.py
│   │   │   │   │   └── so_service.py
│   │   │   │   ├── strategies/
│   │   │   │   │   ├── aetna_strategy.py
│   │   │   │   │   ├── ambetter_strategy.py
│   │   │   │   │   ├── base_strategy.py
│   │   │   │   │   ├── molina_strategy.py
│   │   │   │   │   └── oscar_strategy.py
│   │   │   │   └── WSClient/
│   │   │   │       └── __init__.py
│   │   ├── company_sync_settings/
│   │   │   ├── __init__.py
│   │   │   ├── company_sync_settings.js
│   │   │   ├── company_sync_settings.json
│   │   │   ├── company_sync_settings.py
│   │   │   └── test_company_sync_settings.py
│   ├── overrides/
│   │   ├── contact.py
│   │   └── exception/
│   │       ├── base_document_exist.py
│   │       └── sync_error.py
│   ├── workspace/
│   │   └── company_sync/
│   │       └── company_sync.json
├── config/
│   ├── __init__.py
├── hooks.py
├── installer.py
├── modules.txt
├── patches.txt
├── public/
│   ├── .gitkeep
│   └── js/
│       └── setup_wizard.js
├── pyproject.toml
├── README.md
├── setup/
│   ├── __init__.py
│   └── setup_wizard/
│       ├── __init__.py
│       ├── operations/
│       │   ├── __init__.py
│       │   └── install_fixtures.py
│       ├── setup_wizard.py
├── templates/
│   ├── __init__.py
│   └── pages/
│       └── __init__.py
```

### Key Components

-   **`company_sync_scheduler` DocType:** Manages the scheduling and configuration of synchronization tasks.
    -   Includes configurations for database connections, field mappings, and synchronization strategies.
-   **`company_sync_log` DocType:** Logs synchronization events and errors, providing a detailed history of synchronization activities.
-   **`company_sync_settings` DocType:** Stores global settings for the Company Sync application, such as API keys and connection parameters.
-   **`syncer` Directory:** Contains the core synchronization logic, including handlers, processors, and services.
    -   **Handlers:** Manage communication with external systems, such as VTiger CRM.
    -   **Processors:** Transform data between different formats and schemas.
    -   **Services:** Provide utility functions for data access and manipulation.
-   **`config` Directory:** Contains configuration files for field mappings and handler configurations.
-   **`database` Directory:** Manages database connections and transactions.
-   **`models` Directory:** Defines data models for interacting with VTiger CRM.

## License

MIT License
