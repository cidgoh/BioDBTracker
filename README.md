# BioDBTracker

This tool is designed to track and log versions and details of bioinformatics databases. It provides a streamlined way to monitor changes, with results stored in an SQLite database or directly added to a Google Sheet for easy sharing and collaboration.

## Features

- Track and log versions of bioinformatics databases.
- Store results in an SQLite database for local access.
- Directly integrate with Google Sheets for sharing and collaboration.
- Monitor and document changes efficiently.

## Requirements

Ensure you have Python installed. We recommend using Conda for managing dependencies. See the included `environment.yml` file for setting up the environment.

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/cidgoh/BioDBTracker
    cd BioDBTracker
    ```

2. Set up the Conda environment:

    ```bash
    conda env create -f environment.yml
    conda activate BioDBTracker
    ```

3. Install any additional dependencies if needed:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script with the following command:

```bash
python scan_cidgoh_db.py -i dir1 dir2 -db database_name -gs -gsn google_sheet -gss google_sheet_name -gsc database-cidgoh-1dbcf7c8bf62.json
```

### Command-Line Arguments

- `-i` : Specify input directories (e.g., dir1, dir2).
- `-db` : Name of the database to use.
- `-gs` : Enable Google Sheets integration.
- `-gsn` : Specify the Google Sheet name.
- `-gss` : Specify the sheet name within the Google Sheet.
- `-gsc` : Provide the path to the Google Sheets credential JSON file.

### Example

Here's an example command:

```bash
python scan_cidgoh_db.py -i samples/input1 samples/input2 -db sample_db -gs -gsn MyGoogleSheet -gss Sheet1 -gsc my-google-credentials.json
```
## Database Versioning and Information Management

This folder contains various databases and their respective version information. Each database directory includes a `version.yml` file to track key details such as version number, source, and additional notes. This helps ensure transparency and consistency when sharing or updating databases.

### Folder Structure

The folder structure is designed to organize databases by name and version. For example:

```
DatabaseName/
   ├── v1/
   │    ├── version.yml
   │    └── [other files or subdirectories]
   ├── v2/
   │    ├── version.yml
   │    └── [other files or subdirectories]
   └── custom/
        ├── version.yml
        └── [other files or subdirectories]
```

### Instructions for Adding a Database

1. **Create a Folder:**
   - Create a folder for the database (e.g., `DatabaseName`).
   - Inside this folder, create subfolders for each version (e.g., `v1`, `v2`, etc.).

2. **Add `version.yml`:**
   - In each version's folder, add a `version.yml` file to describe the database details.
   - Use the provided template for consistency.

3. **Template for `version.yml`:**
   ```yaml
   database_info:
     name: [Database Name]
     version: [Database Version]
     date: [Date of Creation/Update]
     downloaded_from: [Source or DOI]
     downloaded_by: [Your Initials]
     tested_by: [Tester Initials, if applicable]
     note: [Any additional information or notes]
   ```
   - An example template for `version.yml` is provided in this directory. Simply copy the template and replace its content.

   - For custom databases, assign a custom version number and describe the source of the data in the `note` field.

   **Example for a Custom Database:**
   ```yaml
   database_info:
     name: k2_refSeq-March-01-2024_mouse_50G
     version: v1.0-custom
     date: "2024-01-2024"
     downloaded_from: "RefSeq"
     downloaded_by: "JD"
     tested_by: "MT"
     note:  This database was built using Kraken 2 version 2.1.2. It includes genomes from RefSeq release 221, covering the following: Archaea, Bacter, Human, Plasmid, UniVec_Core, Viral genomes

   ```

4. **Zipped Files:**
   - Zipped files can remain zipped within the version folder.
   - Ensure the `version.yml` file exists alongside the zipped files.

## License

MIT License.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any proposed changes.

## Contact

For questions or suggestions, reach out to duanjun1981@gmail.com.