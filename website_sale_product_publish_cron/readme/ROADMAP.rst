With this module, if a user unpublishes products that were set to remain published until
a specified expected_unpublish_date, the system will republish them during the next cron run.
The same scenario applies to manually publishing timeframe products. It's essential to update both
the expected_publish_date and expected_unpublish_date if a user decides to manually publish or unpublish for timeframe products.
