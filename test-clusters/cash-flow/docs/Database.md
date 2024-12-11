# Accessing the user database via docker-compose

```bash
docker compose exec -it user-db psql -U postgres
```
## Connect to the user_data table
```bash
\c user_data
```

## Show the users: 
```sql
select * from users;
```

## Delete the users:
```sql
delete from users;
```

# Accessing the transactions database via docker-compose
```bash
docker compose exec -it tx-db psql -U postgres
```

## Show all transactions
```sql
select * from transactions;
```

## Delete all transactions
```sql
delete from users;
```


