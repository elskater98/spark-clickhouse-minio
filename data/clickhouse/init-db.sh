#!/usr/bin/env bash
clickhouse-client --user $CLICKHOUSE_ADMIN_USER --password $CLICKHOUSE_ADMIN_PASSWORD --query "CREATE DATABASE IF NOT EXISTS example_db;"
