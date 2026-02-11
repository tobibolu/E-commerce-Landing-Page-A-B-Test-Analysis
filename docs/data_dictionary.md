# Data Dictionary

## ab_data.csv
- `user_id`: Unique experiment user identifier.
- `timestamp`: Exposure/conversion event timestamp.
- `group`: Assigned variant (`control`, `treatment`).
- `landing_page`: Page shown (`old_page`, `new_page`).
- `converted`: Binary conversion outcome (0/1).

## countries.csv
- `user_id`: User identifier.
- `country`: Country code bucket (`US`, `UK`, `CA`).
