#!/usr/bin/env bash
clickhouse-client --user $CLICKHOUSE_ADMIN_USER --password $CLICKHOUSE_ADMIN_PASSWORD --query "CREATE DATABASE IF NOT EXISTS project;"
clickhouse-client --user $CLICKHOUSE_ADMIN_USER --password $CLICKHOUSE_ADMIN_PASSWORD --query "CREATE TABLE project.bookings
(
    num_passengers        Nullable(Int32),
    sales_channel         Nullable(String),
    trip_type             Nullable(String),
    purchase_lead         Nullable(Int32),
    length_of_stay        Nullable(Int32),
    flight_hour           Nullable(Int32),
    flight_day            Nullable(String),
    routes                Nullable(String),
    booking_origin        Nullable(String),
    wants_extra_baggage   Nullable(Bool),
    wants_preferred_seat  Nullable(Bool),
    wants_in_flight_meals Nullable(Bool),
    flight_duration       Nullable(Float32),
    booking_complete      Nullable(Bool)
)
    engine = Memory;

"
