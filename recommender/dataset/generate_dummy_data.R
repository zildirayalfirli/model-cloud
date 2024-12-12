#################################################################
#     
#       Dummy Dataset Generation for Purchase Recommender System
#
#
#################################################################
#install.packages("random")
library(random)
library(clipr)

  # Defining Data Frame
  # list of variables:
  # 1. uid    (string )       : user id, randomly generated string of characters and numeric of length 28
  # 2. email  (string )       : concatenated string of uid and an email domail(just as a placeholder)
  # 3. age    (int)           : users age
  # 4. product_name (string)  : purchased product name
  # 5. product_type (string)  : purchased product type
  # 6. quantity (int)         : quantity of product purchased
  # 7. purchased_price (int)  : unit price of purchased product, in Indonesian Rupiah
  # 8. purchase_date (string) : ISO 8601 date (%Y-%m-%d)
  # 9. purchase_address (string) : location of purchase, will mostly be empty
  # 10. long 
  # 11. lat


purchase_history <- data.frame(
  uid = c(""),
  email = c(""),
  age = c(0),
  product_name = c(""),
  product_type = c(""),
  quantity = c(0),
  purchase_price = c(0),
  purchase_date = c(""),
  purchase_address = c(""),
  long = c(0.0),
  lat = c(0.0)
)

#################################################################
# 1. generate random uid
#################################################################
generate_random_string <- function(length) {
  # Generates a random string of the specified length containing both characters and numbers for dummy uid.
  # 
  # Args:
  #   length: The desired length of the string.
  # 
  # Returns:
  #   A random string of the specified length.
  
  
  letters <- letters
  digits <- 0:9
  characters <- c(letters, digits)
  
  random_string <- paste(sample(characters, length, replace = TRUE), collapse = "")
  return(random_string)
}

purchase_history[1:100,"uid"] <- ""

for(i in 1:nrow(purchase_history)){
  purchase_history[i,"uid"] = generate_random_string(28)
}

#################################################################
# 2. generate random email
#################################################################
for(i in 1:nrow(purchase_history)){
  purchase_history[i,"email"] = paste0(generate_random_string(5), "@gmail.com")
}

#################################################################
# 3. generate random age
#################################################################
generate_left_skewed_int <- function(min, max, n) {
  # Generate random quantiles from a uniform distribution skewed to the left
  quantiles <- runif(n, min = 0, max = 0.8)
  
  random_ints <- floor(quantiles * (max - min + 1)) + min
  
  return(random_ints)
}

purchase_history$age <- generate_left_skewed_int(12,71,nrow(purchase_history))
hist(purchase_history$age)

#################################################################
# randomly repeat rows
random_indices <- sample(1:100, 500, replace = TRUE)
df_repeated = purchase_history[random_indices,]

#################################################################
# 4. generate product_name, product_type, and product_price
#################################################################
product_names <- c("AQUA AIR MINERAL 1500",
                   "AQUA AIR MINERAL 600",
                   "POKKA GREEN TEA 450",
                   "GATSBY CLG. D/OCN. 175",
                   "WETZ WIPES 30 GRNTEA",
                   "TESSA FAC LOONEY TP3",
                   "POKKA GRN TEA NS 450",
                   "KP POLOS",
                   "SQ GREENTEA 22G",
                   "ULTRA FC 250 ML",
                   "INDOMIE RDG 91G",
                   "GD GCPN 250ML",
                   "GG SURYA 12",
                   "YUPI NEON 45G",
                   "CHUPA GUM FR11G",
                   "KNZLR SGL GJ65G",
                   "RTE ONGR AY PDS",
                   "SR TWR SPC",
                   "GG SURYA CKT16",
                   "ICHITAN MLK BRWN 300",
                   "INDF IC RB RD VLT55",
                   "LEMNRL AIR600ML",
                   "NIPISMADU 330ML",
                   "KNZLER SNGLES ORG 65",
                   "KANZER BAKSO HOT 55G",
                   "MD ALMOND RING",
                   "S.BRD TA CHOCO FLAT",
                   "KUSUKA LH 60G",
                   "CIMORY BLYC120G",
                   "BENG2 SHARE 10S",
                   "CHUPA BELT 8G",
                   "FOREST PCH480ML",
                   "CCBB STR STK 5S",
                   "IDM KCNG BUMBU 150G",
                   "OREO ORIGINAL 119.5G",
                   "S.BRD TA POLO KEJU",
                   "B/P MANGGA HARUM MNS",
                   "TEREA PRPL WAVE 20S"
                   )

product_prices <- c(6600,3500,7300,22000,17900,7500,10200,500,13400,7500,3100,7700,27200,5500,5500,8900,10000,15000,36700,
                    9900,4500,3700,3900,9000,9000,7500, 10000,6500,8500,16400,3000,9300,3500,16800,9900,10000,9000,
                    30000)

writeClipboard(product_names)

products <- read_clip_tbl()

for(i in 1:nrow(df_repeated)){
  temp_num = sample(1:38, 1)
  
  df_repeated[i,"product_name"] = products[temp_num,"product_name"]
  df_repeated[i,"product_type"] = products[temp_num,"product_type"]
  df_repeated[i,"purchase_price"] = products[temp_num,"purchased_price"]
}

#################################################################
# 5. generate random quantity
#################################################################
df_repeated$quantity <- generate_left_skewed_int(1,5,nrow(df_repeated))

#################################################################
# 6. generate random dates
#################################################################
random_dates <- vector("character", 500)

for (i in 1:500) {
  random_day <- sample(1:365, 1)
  random_date <- as.Date(paste0(2024, "-", random_day), format = "%Y-%j")
  random_dates[i] <- format(random_date, "%Y-%m-%d")
}

df_repeated$purchase_date <- random_dates

df_repeated$purchase_address <- ""


#################################################################
# 7. generate random long lat
#################################################################
base_long = 110.435700
base_lat = -7.056400

generate_random_coords <- function(lat, lon, radius) {
  # Generate random angle in radians
  angle <- runif(1, 0, 2 * pi)
  
  # Generate random distance within the radius
  distance <- runif(1, 0, radius)
  
  # Calculate new latitude and longitude using the Haversine formula
  new_lat <- asin(sin(lat) * cos(distance / 6371) + cos(lat) * sin(distance / 6371) * cos(angle))
  new_lon <- lon + atan2(sin(angle) * sin(distance / 6371) * cos(lat), cos(distance / 6371) - sin(lat) * sin(new_lat))
  
  return(list(lat=new_lat, long=new_lon))
}

random_points <- data.frame(
  lat = c(0.0),
  long = c(0.0)
  )

for(i in 1:nrow(df_repeated)){
  temp_random_points = generate_random_coords(base_lat, base_long, 10)
  
  random_points[i,"lat"] = temp_random_points[[1]]
  random_points[i, "long"] = temp_random_points[[2]]
}

df_repeated$lat = random_points$lat
df_repeated$long = random_points$long

write.csv(df_repeated, file = "C:/Temp/UNI 2024-2025/Sem 7/Bangkit/Capstone/OCR Struk Belanja/recommender/purchase_history.csv",
          row.names = FALSE)
