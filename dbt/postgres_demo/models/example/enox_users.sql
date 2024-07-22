with source as (

    {#-
    Normally we would select from the table here, but we are using seeds to load
    our data in this project
    #}
    select * from {{ ref('raw_enox_users') }}

),

{{ config(materialized='table') }}
enox_users as (
    select
        owner_id,
        first_name,
        last_name,
        birth_date,
        device_id,
        street,
        house_nr,
        town,
        post_code,
        country_code
    from source
)

select * from enox_users