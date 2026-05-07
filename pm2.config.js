module.exports = {
  apps: [
    {
      name: 'meridian-web',
      script: 'gunicorn',
      args: 'app:app --bind 0.0.0.0:8080 --workers 2 --timeout 120',
      interpreter: 'none',
      env: {
        FLASK_ENV: 'production',
      },
    },
    {
      name: 'meridian-weekly-send',
      script: 'scripts/send_weekly_readings.py',
      interpreter: 'python3',
      cron_restart: '0 6 * * 1', // Every Monday 6am UTC
      autorestart: false,
    },
    {
      name: 'meridian-saturn-check',
      script: 'scripts/saturn_return_check.py',
      interpreter: 'python3',
      cron_restart: '0 7 * * *', // Daily 7am UTC
      autorestart: false,
    },
  ],
};
