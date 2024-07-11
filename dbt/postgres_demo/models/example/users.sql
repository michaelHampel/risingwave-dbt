with source as (

    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    select * from {{ ref('raw_users') }}

),

{{ config(materialized='table') }}
users as (
    select
        id,
        first_name,
        last_name,
        age
    from source
)

select * from users