# Data Collection Engine  
## 1.1 Functional Overview  
The engine consists of two core modules:  
1. **File Download Module**: Pulls specified files from the data center to the local server based on a configuration table.  
2. **Data Loading Module**: Writes file data into target database tables using configuration scripts.  

---  
## 2. Detailed Design  
### 3.1 File Download Module  
**Process Description:**  
- **Step 1**: The engine downloads data files daily from the FTP directory. The file path rules are specified in Interface Design 1.  
- **Step 2**: The engine reads the configuration table `t_download_config` under the DPM user in the OceanBase database using the following SQL to retrieve the files to be downloaded:  
  ```sql  
  SELECT File_name FROM dpm.t_download_config WHERE status = 1  
  ```  
- **Step 3**: Based on the query results, the engine scans the FTP directory for files matching the specified names and initiates the download to the local server.  
- **Step 4**: The local storage path follows the configuration in Interface Design 3.  
- **Step 5**: The completion of the download is verified by comparing file sizes.  
- **Step 6**: After successful download, the engine automatically inserts a record into the table specified in Interface Design 4 to log the completion.  

**Interface Design:**  
1. **Data Center File Path Rules**  
   - Example file storage path: `172.168.77.119/data/crmpro/YYYYMMDD`  
   - The last directory level represents the previous trading day's date (e.g., `20250513`). The engine must automatically fetch the latest date directory daily.  

2. **Download Configuration Table Design**  
   - Table name: `t_download_config`  
   - Table structure:  

     | Column Name | Type         | Description |  
     |-------------|--------------|-------------|  
     | Table_name  | Varchar(100) | Target table name |  
     | File_name   | Varchar(200) | File name to download (supports wildcards, e.g., `INT_D_NEW_CRM_*`) |  
     | status      | Char(1)      | Status (`1`-enabled, `0`-disabled) |  

3. **Local Server Configuration**  
   - Configuration file format (JSON):  
     ```json  
     {  
       "agent_url": "172.168.77.119/data",  // Root path of data center files  
       "agent_user": "admin",               // Login user  
       "pwd": "******",                     // Login password  
       "local_dir": "/opt/data_engine/download" // Local storage directory  
     }  
     ```  

4. **File Download and Verification**  
   - After download completion, a record is inserted into the `t_ftp_download_result` table with the following structure:  

     | Column Name   | Type         | Description |  
     |---------------|--------------|-------------|  
     | Data          | Number(8)    | Data date (YYYYMMDD) |  
     | Owner         | Varchar(20)  | Owning user (e.g., `SRC_DPM`) |  
     | Table_name    | Varchar(100) | Table name |  
     | status        | Char(1)      | Status (`1`-completed, `2`-incomplete) |  
     | finish_time   | Date         | Completion time (accurate to seconds) |  

   - Example data:  

     | Data      | Owner    | Table_name            | status | finish_time          |  
     |-----------|----------|-----------------------|--------|----------------------|  
     | 20250512  | SRC_DPM  | INT_D_NEW_CRM_KPI_CUST | 1      | 2025-05-13 00:12:01  |  

---  
### 3.2 Data Loading Module  
**Process Description:**  
- **Step 1**: The data files pushed by the data warehouse follow a standard format. For example, the file `INT_D_KPI_HZ_CUST.dat` contains:  
  ```  
  Biz_dt!|cust_num!|cust_dept  
  20250522!|1000000!|8006  
  20250522!|1000002!|8012  
  20250522!|1000001!|8106  
  ```  
  **File Content Parsing:**  
  - The first row contains field names, separated by `!|`.  
  - Subsequent rows contain data, with each field separated by `!|`. The number of fields in each data row matches the first row.  

- **Step 2**: Users write script files to load data into tables. The script format is as follows:  
  - **Script file name**: `<data_filename>.sql`  
  - **Script template**:  
    ```sql  
    INSERT INTO table_name  
    (field1, field2, field3)  
    SELECT  
    Val[1],  
    Val[2],  
    Val[3]  
    FROM c6_oceanbase.data_filename.dat  
    ```  
  - **Example**: To load data from `INT_D_KPI_HZ_CUST.dat` into the table `SRC_SWHY.INT_D_KPI_HZ_CUST`, the script would be:  
    ```sql  
    INSERT INTO SRC_SWHY.INT_D_KPI_HZ_CUST  
    (Biz_dt, cust_num, cust_dept)  
    SELECT  
    Val[1],  
    Val[2],  
    Val[3]  
    FROM INT_D_KPI_HZ_CUST.dat  
    ```  
  - **Note**: This script is not strict SQL but a configuration file resembling SQL, designed to help developers easily map file data to tables using SQL-like syntax.  

After insertion is complete, the engine's workflow concludes.
