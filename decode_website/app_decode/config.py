class Config(object):
    # Defines the random bytes a token contains
    # 32 is recommended in Python.secrets docs
    TOKEN_N_BYTES = 32
    # Expire duration of a token since its issue, in seconds
    TOKEN_LIFESPAN = 300
    # MySQL server URI
    SQLALCHEMY_DATABASE_URI = 'mysql://decode:-v19hVITZ3ttCMqqe89H5G_S7yE4HaoLvf-DceMMnFo@localhost:3306/decode?charset=utf8mb4'

    # These usernames have special use in this application
    # These passwords are used to initialize application
    # Passwords are stored in database and should be changed using admin portal
    # Admin portal
    ADMIN_PORTAL_USERNAME = 'cuhkszadmin'
    ADMIN_PORTAL_PASSWORD = 'gFjkVp_6hxyHqA4vb-BVzdXWZ9X_xxo_0e1DWQRuhmU'
    # Token issue API
    ISSUE_TOKEN_USERNAME = 'icuhk'
    ISSUE_TOKEN_PASSWORD = 'pStxpAuv5Ld-wKRz68o7NBNyj64fyn62nh8Ak1Xx60Q'
    # Token verify API
    VERIFY_TOKEN_USERNAME = 'sribd_la'
    VERIFY_TOKEN_PASSWORD = '1cVXyAIJTjTwUngAMbD4s4H4p_x45nRVEG0EDDek4c0'

    # These two are used in email system
    # These passwords are used to initialize application
    # Passwords are stored in database and should be changed using email admin portal
    # Email admin
    EMAIL_ADMIN_USERNAME = 'supervisor'
    EMAIL_ADMIN_PASSWORD = 'oKjrLb6Bm8xFvJBVK3N5iYym9lkq5e1btxA_PSbkn_I'
    # Email user
    EMAIL_USER_USERNAME = 'laemail'
    EMAIL_USER_PASSWORD = 'aoc_SkpB_ZwKFWHod37iYgTfC6LyNgrfD-3D9QNpE4Q'
