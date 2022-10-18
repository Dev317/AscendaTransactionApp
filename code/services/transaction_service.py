# CREATE
# invoked by CSV processor, invoked by UI (admin)

# READ
# invoked by reward_service

# UPDATE
# ? luxury

# DELETE
# ? luxury

# When threshold transaction records are added, will invoke reward_service to generate new rewards
# after bulk processing a csv, will sort the records by card type then date,
#  then invoke reward service in batches
#  (to improve speed by caching, where many txs with the same policy can be calculated at the same time