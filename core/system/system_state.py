# ============================================
# GLOBAL SYSTEM STATE
# ============================================

AUTH_RUNNING = False

ENROLL_RUNNING = False

DOOR_BUSY = False

EXIT_ENABLED = True

SYSTEM_READY = True


# ============================================
# AUTH STATE
# ============================================

def start_auth():

    global AUTH_RUNNING
    global EXIT_ENABLED

    AUTH_RUNNING = True

    EXIT_ENABLED = False

    print("[STATE] AUTH STARTED")


def stop_auth():

    global AUTH_RUNNING
    global EXIT_ENABLED

    AUTH_RUNNING = False

    EXIT_ENABLED = True

    print("[STATE] AUTH STOPPED")


# ============================================
# ENROLL STATE
# ============================================

def start_enroll():

    global ENROLL_RUNNING
    global EXIT_ENABLED

    ENROLL_RUNNING = True

    EXIT_ENABLED = False

    print("[STATE] ENROLL STARTED")


def stop_enroll():

    global ENROLL_RUNNING
    global EXIT_ENABLED

    ENROLL_RUNNING = False

    EXIT_ENABLED = True

    print("[STATE] ENROLL STOPPED")


# ============================================
# DOOR STATE
# ============================================

def set_door_busy():

    global DOOR_BUSY

    DOOR_BUSY = True

    print("[STATE] DOOR BUSY")


def clear_door_busy():

    global DOOR_BUSY

    DOOR_BUSY = False

    print("[STATE] DOOR READY")
