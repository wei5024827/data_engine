from datetime import datetime, timedelta

def get_target_date():
    return (datetime.now() - timedelta(days=1)).strftime('%Y%m%d')
