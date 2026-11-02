idf_component_register(SRCS "main.c"
                    INCLUDE_DIRS "."
                    EMBED_TXTFILES "index.html"
                    REQUIRES esp_http_server esp_wifi nvs_flash esp_netif esp_event driver esp_driver_i2s esp_driver_gpio esp_timer)
