HOUR_CHOICES = [x for x in range(7, 20)]  #[7, 17]
PERIOD_CHOICES = [0, 1, 2]
DAY_WEEK_CHOICES = [0, 1, 2, 3, 4]

#regexes
NAME_RE = "^[a-zA-Zñá-úÁ-Úü]([.](?![.])|[ ](?![ .])|[a-zA-Zñá-úÁ-Úü])*$"
EMAIL_RE = "^a[0-9]{8}@tec.mx"
MAJOR_RE = "^[A-Z]*$"

#constants for lookup in Period table
START_DATE_FIELDS = ["beginning_first_period", "beginning_second_period", "beginning_third_period"]
END_DATE_FIELDS = ["ending_first_period", "ending_second_period", "ending_third_period"]