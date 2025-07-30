# Data IDs for Charger from signalr stream

from enum import Enum


class ChargerStreamData(Enum):
    state_selfTestResult = 1  # OK or error codes [String] ['Admin', 'Partner', 'User']
    state_selfTestDetails = 2  # JSON with details from self-test [String] ['Admin', 'Partner']
    state_debugLog = 5
    state_wifiEvent = 10  # Enum with WiFi event codes. Requires telemetry debug mode. Will be updated on WiFi events when using cellular, will otherwise be reported in ChargerOfflineReason [Integer] ['Admin', 'Partner']
    state_chargerOfflineReason = 11  # Enum describing why charger is offline [Integer] ['Admin', 'Partner', 'User']
    state_easeeLinkCommandResponse = (
        13  # Response on a EaseeLink command sent to another devic [Integer] ['Admin', 'Partner']
    )
    state_easeeLinkDataReceived = 14  # Data received on EaseeLink from another device [String] ['Admin', 'Partner']
    config_localPreAuthorizeEnabled = (
        15  # Preauthorize with whitelist enabled. Readback on setting [event] [Boolean] ['Admin', 'Partner', 'User']
    )
    config_localAuthorizeOfflineEnabled = 16  # Allow offline charging for whitelisted RFID token. Readback on setting [event] [Boolean] ['Admin', 'Partner', 'User']
    config_allowOfflineTxForUnknownId = 17  # Allow offline charging for all RFID tokens. Readback on setting [event] [Boolean] ['Admin', 'Partner', 'User']
    config_erraticEVMaxToggles = 18  # 0 == erratic checking disabled, otherwise the number of toggles between states Charging and Charging Complate that will trigger an error [Integer] ['Admin', 'Partner']
    config_backplateType = 19  # Readback on backplate type [Integer] ['Admin', 'Partner']
    config_siteStructure = 20  # Site Structure [boot] [String] ['Admin', 'Partner']
    config_detectedPowerGridType = (
        21  # Detected power grid type according to PowerGridType table [boot] [Integer] ['Admin', 'Partner', 'User']
    )
    config_circuitMaxCurrentP1 = 22  # Set circuit maximum current [Amperes] [Double] ['Admin', 'Partner', 'User']
    config_circuitMaxCurrentP2 = 23  # Set circuit maximum current [Amperes] [Double] ['Admin', 'Partner', 'User']
    config_circuitMaxCurrentP3 = 24  # Set circuit maximum current [Amperes] [Double] ['Admin', 'Partner', 'User']
    config_location = 25  # Location coordinate [event] [Position] ['Admin', 'Partner']
    config_siteIDString = 26  # Site ID string [event] [String] ['Admin', 'Partner']
    config_siteIDNumeric = 27  # Site ID numeric value [event] [Integer] ['Admin', 'Partner']
    config_rfidAuthTimeoutSec = 28  # Timeout for backend to send authorization reply. After timeout offline rules apply. [Integer] ['Admin', 'Partner']
    state_lockCablePermanently = 30  # Lock type2 cable permanently [Boolean] ['Admin', 'Partner', 'User']
    config_isEnabled = 31  # Set true to enable charger, false disables charger [Boolean] ['Admin', 'Partner', 'User']
    state_temperatureMonitorState = (
        32  # State of the monitor: OFF=0, MONITORING=-1, ACTIVE=1 [Integer] ['Admin', 'Partner']
    )
    config_circuitSequenceNumber = 33  # Charger sequence number on circuit [Integer] ['Admin', 'Partner']
    config_singlePhaseNumber = 34  # Phase to use in 1-phase charging [Integer] ['Admin', 'Partner']
    config_enable3PhasesDEPRECATED = 35  # Allow charging using 3-phases [Boolean] ['Admin', 'Partner', 'User']
    config_wiFiSSID = 36  # WiFi SSID name [String] ['Admin', 'Partner', 'User']
    config_enableIdleCurrent = 37  # Charger signals available current when EV is done charging [user option][event] [Boolean] ['Admin', 'Partner', 'User']
    config_phaseMode = 38  # Phase mode on this charger. 1-Locked to 1-Phase, 2-Auto, 3-Locked to 3-phase(only Home) [Integer] ['Admin', 'Partner', 'User']
    config_forcedThreePhaseOnITWithGndFault = 39  # Default disabled. Must be set manually if grid type is indeed three phase IT [Boolean] ['Admin', 'Partner']
    config_ledStripBrightness = 40  # LED strip brightness, 0-100% [Integer] ['Admin', 'Partner', 'User']
    config_localAuthorizationRequired = 41  # Local RFID authorization is required for charging [user options][event] [Boolean] ['Admin', 'Partner', 'User']
    config_authorizationRequired = 42  # Authorization is requried for charging [Boolean] ['Admin', 'Partner', 'User']
    config_remoteStartRequired = 43  # Remote start required flag [event] [Boolean] ['Admin', 'Partner', 'User']
    config_smartButtonEnabled = 44  # Smart button is enabled [Boolean] ['Admin', 'Partner', 'User']
    config_offlineChargingMode = 45  # Charger behavior when offline [Integer] ['Admin', 'Partner', 'User']
    state_ledMode = 46  # Charger LED mode [event] [Integer] ['Admin', 'Partner', 'User']
    config_maxChargerCurrent = 47  # Max current this charger is allowed to offer to car (A). Non volatile. [Double] ['Admin', 'Partner', 'User']
    state_dynamicChargerCurrent = (
        48  # Max current this charger is allowed to offer to car (A). Volatile [Double] ['Admin', 'Partner', 'User']
    )
    state_offlineMaxCircuitCurrentP1 = (
        50  # Maximum circuit current P1 when offline [event] [Integer] ['Admin', 'Partner', 'User']
    )
    state_offlineMaxCircuitCurrentP2 = (
        51  # Maximum circuit current P2 when offline [event] [Integer] ['Admin', 'Partner', 'User']
    )
    state_offlineMaxCircuitCurrentP3 = (
        52  # Maximum circuit current P3 when offline [event] [Integer] ['Admin', 'Partner', 'User']
    )
    config_releaseCableAtPowerOff = 54  # Release Cable At Power Off [Boolean] ['Admin', 'Partner']
    config_listenToControlPulse = 56  # True = charger needs control pulse to consider itself online. Readback on charger setting [event] [Boolean] ['Admin', 'Partner']
    config_controlPulseRTT = 57  # Control pulse round-trip time in milliseconds [Integer] ['Admin', 'Partner']
    schedule_chargingSchedule = 62  # Charging schedule [json] [String] ['Admin', 'Partner', 'User']
    config_pairedEqualizer = 65  # Paired equalizer details [String] ['Admin', 'Partner']
    state_wiFiAPEnabled = (
        68  # True if WiFi Access Point is enabled, otherwise false [Boolean] ['Admin', 'Partner', 'User']
    )
    state_pairedUserIDToken = (
        69  # Observed user token when charger put in RFID pairing mode [event] [String] ['Admin', 'Partner', 'User']
    )
    state_circuitTotalAllocatedPhaseConductorCurrentL1 = 70  # Total current allocated to L1 by all chargers on the circuit. Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_circuitTotalAllocatedPhaseConductorCurrentL2 = 71  # Total current allocated to L2 by all chargers on the circuit. Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_circuitTotalAllocatedPhaseConductorCurrentL3 = 72  # Total current allocated to L3 by all chargers on the circuit. Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_circuitTotalPhaseConductorCurrentL1 = 73  # Total current in L1 (sum of all chargers on the circuit) Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_circuitTotalPhaseConductorCurrentL2 = 74  # Total current in L2 (sum of all chargers on the circuit) Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_circuitTotalPhaseConductorCurrentL3 = 75  # Total current in L3 (sum of all chargers on the circuit) Sent in by master only [Double] ['Admin', 'Partner', 'User']
    state_numberOfCarsConnected = 76  # Number of cars connected to this circuit [Integer] ['Admin', 'Partner']
    state_numberOfCarsCharging = 77  # Number of cars currently charging [Integer] ['Admin', 'Partner']
    state_numberOfCarsInQueue = (
        78  # Number of cars currently in queue, waiting to be allocated power [Integer] ['Admin', 'Partner']
    )
    state_numberOfCarsFullyCharged = 79  # Number of cars that appear to be fully charged [Integer] ['Admin', 'Partner']
    state_chargerFirmware = 80  # Embedded software package release id [boot] [Integer] ['Admin', 'Partner', 'User']
    state_ICCID = 81  # SIM integrated circuit card identifier [String] ['Admin', 'Partner']
    state_modemFwId = 82  # Modem firmware version [String] ['Admin', 'Partner']
    state_OTAErrorCode = 83  # OTA error code, see table [event] [Integer] ['Admin', 'Partner']
    state_mobileNetworkOperator = 84  # Current mobile network operator [pollable] [String] ['Admin', 'Partner']
    state_rebootReason = 89  # Reason of reboot. Bitmask of flags. [Integer] ['Admin', 'Partner']
    state_powerPCBVersion = 90  # Power PCB hardware version [Integer] ['Admin', 'Partner']
    state_comPCBVersion = 91  # Communication PCB hardware version [Integer] ['Admin', 'Partner']
    state_reasonForNoCurrent = 96  # Enum describing why a charger with a car connected is not offering current to the car [Integer] ['Admin', 'Partner', 'User']
    state_loadBalancingNumberOfConnectedChargers = 97  # Number of connected chargers in the load balancin. Including the master. Sent from Master only. [Integer] ['Admin', 'Partner']
    state_UDPNumOfConnectedNodes = (
        98  # Number of chargers connected to master through UDP / WIFI [Integer] ['Admin', 'Partner']
    )
    state_localConnection = 99  # Slaves only. Current connection to master, 0 = None, 1= Radio, 2 = WIFI UDP, 3 = Radio and WIFI UDP [Integer] ['Admin', 'Partner']
    state_pilotMode = 100  # Pilot Mode Letter (A-F) [event] [String] ['Admin', 'Partner']
    state_carConnectedDEPRECATED = 101  # Car connection state [Boolean] ['Admin', 'Partner']
    state_smartCharging = (
        102  # Smart charging state enabled by capacitive touch button [event] [Boolean] ['Admin', 'Partner', 'User']
    )
    state_cableLocked = 103  # Cable lock state [event] [Boolean] ['Admin', 'Partner', 'User']
    state_cableRating = 104  # Cable rating read [Amperes][event] [Integer] ['Admin', 'Partner', 'User']
    state_pilotHigh = 105  # Pilot signal high [Volt][debug] [Integer] ['Admin', 'Partner']
    state_pilotLow = 106  # Pilot signal low [Volt][debug] [Integer] ['Admin', 'Partner']
    state_backPlateID = 107  # Back Plate RFID of charger [boot] [String] ['Admin', 'Partner']
    state_userIDTokenReversed = 108  # User ID token string from RFID reading [event](NB! Must reverse these strings) [String] ['Admin', 'Partner']
    state_chargerOpMode = (
        109  # Charger operation mode according to charger mode table [event] [Integer] ['Admin', 'Partner', 'User']
    )
    state_outputPhase = 110  # Active output phase(s) to EV according to output phase type table. [event] [Integer] ['Admin', 'Partner', 'User']
    state_dynamicCircuitCurrentP1 = 111  # Dynamically set circuit maximum current for phase 1 [Amperes][event] [Double] ['Admin', 'Partner', 'User']
    state_dynamicCircuitCurrentP2 = 112  # Dynamically set circuit maximum current for phase 2 [Amperes][event] [Double] ['Admin', 'Partner', 'User']
    state_dynamicCircuitCurrentP3 = 113  # Dynamically set circuit maximum current for phase 3 [Amperes][event] [Double] ['Admin', 'Partner', 'User']
    state_outputCurrent = 114  # Available current signaled to car with pilot tone [Double] ['Admin', 'Partner', 'User']
    state_deratedCurrent = 115  # Available current after derating [A] [Double] ['Admin', 'Partner', 'User']
    state_deratingActive = 116  # Available current is limited by the charger due to high temperature [event] [Boolean] ['Admin', 'Partner', 'User']
    state_debugString = 117  # Debug string [String] ['Admin', 'Partner']
    state_errorString = 118  # Descriptive error string [event] [String] ['Admin', 'Partner', 'User']
    state_errorCode = 119  # Error code according to error code table [event] [Integer] ['Admin', 'Partner', 'User']
    state_totalPower = 120  # Total power [kW][telemetry] [Double] ['Admin', 'Partner', 'User']
    state_sessionEnergy = 121  # Session accumulated energy [kWh][telemetry] [Double] ['Admin', 'Partner', 'User']
    state_energyPerHour = 122  # Accumulated energy per hour [kWh][event] [Double] ['Admin', 'Partner', 'User']
    state_legacyEvStatus = (
        123  # 0 = not legacy ev, 1 = legacy ev detected, 2 = reviving ev [Integer] ['Admin', 'Partner']
    )
    state_lifetimeEnergy = (
        124  # Accumulated energy in the lifetime of the charger [kWh] [Double] ['Admin', 'Partner', 'User']
    )
    state_lifetimeRelaySwitches = 125  # Total number of relay switches in the lifetime of the charger (irrespective of the number of phases used) [Integer] ['Admin', 'Partner']
    state_lifetimeHours = 126  # Total number of hours in operation [Integer] ['Admin', 'Partner']
    config_dynamicCurrentOfflineFallbackDEPRICATED = (
        127  # Maximum circuit current when offline [event] [Integer] ['Admin', 'Partner']
    )
    state_userIDToken = 128  # User ID token string from RFID reading [event] [String] ['Admin', 'Partner']
    state_ChargingSession = 129  # Charging sessions [json][event] [String] ['Admin', 'Partner']
    state_cellRSSI = 130  # Cellular signal strength [dBm][telemetry] [Integer] ['Admin', 'Partner', 'User']
    state_CellRAT = (
        131  # Cellular radio access technology according to RAT table [event] [Integer] ['Admin', 'Partner']
    )
    state_wiFiRSSI = 132  # WiFi signal strength [dBm][telemetry] [Integer] ['Admin', 'Partner', 'User']
    config_cellAddress = 133  # IP address assigned by cellular network [debug] [String] ['Admin', 'Partner']
    config_wiFiAddress = 134  # IP address assigned by WiFi network [debug] [String] ['Admin', 'Partner']
    config_wiFiType = 135  # WiFi network type letters (G, N, AC, etc) [debug] [String] ['Admin', 'Partner']
    state_localRSSI = 136  # Local radio signal strength [dBm][telemetry] [Integer] ['Admin', 'Partner', 'User']
    state_masterBackPlateID = 137  # Back Plate RFID of master [event] [String] ['Admin', 'Partner']
    state_localTxPower = 138  # Local radio transmission power [dBm][telemetry] [Integer] ['Admin', 'Partner']
    state_localState = 139  # Local radio state [event] [String] ['Admin', 'Partner']
    state_foundWiFi = 140  # List of found WiFi SSID and RSSI values [event] [String] ['Admin', 'Partner', 'User']
    state_chargerRAT = (
        141  # Radio access technology in use: 0 = cellular, 1 = wifi [Integer] ['Admin', 'Partner', 'User']
    )
    state_cellularInterfaceErrorCount = 142  # The number of times since boot the system has reported an error on this interface [poll] [Integer] ['Admin', 'Partner']
    state_cellularInterfaceResetCount = 143  # The number of times since boot the interface was reset due to high error count [poll] [Integer] ['Admin', 'Partner']
    state_wifiInterfaceErrorCount = 144  # The number of times since boot the system has reported an error on this interface [poll] [Integer] ['Admin', 'Partner']
    state_wifiInterfaceResetCount = 145  # The number of times since boot the interface was reset due to high error count [poll] [Integer] ['Admin', 'Partner']
    config_localNodeType = (
        146  # 0-Unconfigured, 1-Master, 2-Extender, 3-End device [Integer] ['Admin', 'Partner', 'User']
    )
    config_localRadioChannel = 147  # Channel nr 0 - 11 [Integer] ['Admin', 'Partner', 'User']
    config_localShortAddress = 148  # Address of charger on local radio network [Integer] ['Admin', 'Partner', 'User']
    config_localParentAddrOrNumOfNodes = (
        149  # If master-Number of slaves connected, If slave- Address parent [Integer] ['Admin', 'Partner', 'User']
    )
    state_tempMax = (
        150  # Maximum temperature for all sensors [Celsius][telemetry] [Integer] ['Admin', 'Partner', 'User']
    )
    state_tempAmbientPowerBoard = 151  # Temperature measured by ambient sensor on bottom of power board [Celsius][event] [Integer] ['Admin', 'Partner']
    state_tempInputT2 = 152  # Temperature at input T2 [Celsius][event] [Integer] ['Admin', 'Partner']
    state_tempInputT3 = 153  # Temperature at input T3 [Celsius][event] [Integer] ['Admin', 'Partner']
    state_tempInputT4 = 154  # Temperature at input T4 [Celsius][event] [Integer] ['Admin', 'Partner']
    state_tempInputT5 = 155  # Temperature at input T5 [Celsius][event] [Integer] ['Admin', 'Partner']
    state_tempOutputN = (
        160  # Temperature at type 2 connector plug for N [Celsius][event] [Integer] ['Admin', 'Partner']
    )
    state_tempOutputL1 = (
        161  # Temperature at type 2 connector plug for L1 [Celsius][event] [Integer] ['Admin', 'Partner']
    )
    state_tempOutputL2 = (
        162  # Temperature at type 2 connector plug for L2 [Celsius][event] [Integer] ['Admin', 'Partner']
    )
    state_tempOutputL3 = (
        163  # Temperature at type 2 connector plug for L3 [Celsius][event] [Integer] ['Admin', 'Partner']
    )
    state_tempRelayN = 164  # Temperature under N relay on ONE [Celsius] [Integer] ['Admin', 'Partner']
    state_tempRelayL = 165  # Temperature under L relay on ONE [Celsius] [Integer] ['Admin', 'Partner']
    state_tempAmbientPowerBoardTop = (
        166  # Temperature measured by ambient sensor on top of power board [Celsius] [Integer] ['Admin', 'Partner']
    )
    state_tempAmbient = 170  # Ambient temperature on COM board [Celsius][event] [Integer] ['Admin', 'Partner']
    state_lightAmbient = 171  # Ambient light from front side [Percent][debug] [Integer] ['Admin', 'Partner']
    state_intRelHumidity = 172  # Internal relative humidity [Percent][event] [Integer] ['Admin', 'Partner']
    state_backPlateLocked = 173  # Back plate confirmed locked [event] [Boolean] ['Admin', 'Partner']
    state_currentMotor = 174  # Motor current draw [debug] [Double] ['Admin', 'Partner']
    state_backPlateHallSensor = 175  # Raw sensor value [mV] [Integer] ['Admin', 'Partner']
    state_inCurrentT2 = (
        182  # Calculated current RMS for input T2 [Amperes][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inCurrentT3 = 183  # Current RMS for input T3 [Amperes][telemetry] [Double] ['Admin', 'Partner', 'User']
    state_inCurrentT4 = 184  # Current RMS for input T4 [Amperes][telemetry] [Double] ['Admin', 'Partner', 'User']
    state_inCurrentT5 = 185  # Current RMS for input T5 [Amperes][telemetry] [Double] ['Admin', 'Partner', 'User']
    state_inVoltageT1T2 = (
        190  # Input voltage RMS between T1 and T2 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT1T3 = (
        191  # Input voltage RMS between T1 and T3 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT1T4 = (
        192  # Input voltage RMS between T1 and T4 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT1T5 = (
        193  # Input voltage RMS between T1 and T5 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT2T3 = (
        194  # Input voltage RMS between T2 and T3 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT2T4 = (
        195  # Input voltage RMS between T2 and T4 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT2T5 = (
        196  # Input voltage RMS between T2 and T5 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT3T4 = (
        197  # Input voltage RMS between T3 and T4 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT3T5 = (
        198  # Input voltage RMS between T3 and T5 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_inVoltageT4T5 = (
        199  # Input voltage RMS between T4 and T5 [Volt][telemetry] [Double] ['Admin', 'Partner', 'User']
    )
    state_nominalVoltage = 200  # Nominal voltage setting for Easee One [Integer] ['Admin', 'Partner', 'User']
    state_outVoltPin1to2 = (
        202  # Output voltage RMS between type 2 pin 1 and 2 [Volt][telemetry] [Double] ['Admin', 'Partner']
    )
    state_outVoltPin1to3 = (
        203  # Output voltage RMS between type 2 pin 1 and 3 [Volt][telemetry] [Double] ['Admin', 'Partner']
    )
    state_outVoltPin1to4 = (
        204  # Output voltage RMS between type 2 pin 1 and 4 [Volt][telemetry] [Double] ['Admin', 'Partner']
    )
    state_outVoltPin1to5 = (
        205  # Output voltage RMS between type 2 pin 1 and 5 [Volt][telemetry] [Double] ['Admin', 'Partner']
    )
    state_outVoltPin2_3 = 206  # Output voltage RMS between type 2 pin 2 and 3 [Volt] [Double] ['Admin', 'Partner']
    state_voltLevel33 = 210  # 3.3 Volt Level [Volt][telemetry] [Integer] ['Admin', 'Partner']
    state_voltLevel5 = 211  # 5 Volt Level [Volt][telemetry] [Integer] ['Admin', 'Partner']
    state_voltLevel12 = 212  # 12 Volt Level [Volt][telemetry] [Integer] ['Admin', 'Partner']
    state_fatalErrorCode = (
        219  # Fatal error code according to error code table [event] [Integer] ['Admin', 'Partner', 'User']
    )
    state_LTERSRP = 220  # Reference Signal Received Power (LTE) [-144 .. -44 dBm] [Integer] ['Admin', 'Partner']
    state_LTESINR = 221  # Signal to Interference plus Noise Ratio (LTE) [-20 .. +30 dB] [Integer] ['Admin', 'Partner']
    state_LTERSRQ = 222  # Reference Signal Received Quality (LTE) [-19 .. -3 dB] [Integer] ['Admin', 'Partner']
    state_chargingSessionStart = 223  # Charging session started [event] [String] ['Admin', 'Partner']
    state_eqAvailableCurrentP1 = (
        230  # Available current for charging on P1 according to Equalizer [Double] ['Admin', 'Partner', 'User']
    )
    state_eqAvailableCurrentP2 = (
        231  # Available current for charging on P2 according to Equalizer [Double] ['Admin', 'Partner', 'User']
    )
    state_eqAvailableCurrentP3 = (
        232  # Available current for charging on P3 according to Equalizer [Double] ['Admin', 'Partner', 'User']
    )
    state_diagnosticsString = 240  # Various diagnostic information for testing. Must be enabled by setting DiagnosticsMode == 256 [String] ['Admin', 'Partner']
    config_wiFiMACAddress = 241  # Device WiFi MAC address
    state_connectedToCloud = 250  # Device is connected to AWS [Boolean] ['Admin', 'Partner', 'User']
    state_cloudDisconnectReason = 251  # AWS DisconnectReason [String] ['Admin', 'Partner', 'User']


# Data IDs for Equalizer from signalr stream
class EqualizerStreamData(Enum):
    state_selfTestResult = 1  # PASSED or error codes [String] ['Admin', 'Partner']
    state_selfTestDetails = 2  # JSON with details from self-test [String] ['Admin', 'Partner']
    state_easeeLinkCommandResponse = (
        13  # Response on a EaseeLink command sent to another devic [Integer] ['Admin', 'Partner']
    )
    state_easeeLinkDataReceived = 14  # Data received on EaseeLink from another device [String] ['Admin', 'Partner']
    state_siteIDNumeric = 19  # Site ID numeric value [event] [Integer] ['Admin', 'Partner']
    config_siteStructure = 20  # Site Structure [boot] [String] ['Admin', 'Partner', 'User']
    state_softwareRelease = 21  # Embedded software package release id [boot] [Integer] ['Admin', 'Partner', 'User']
    state_deviceMode = 23  # Current device mode [Integer] ['Admin', 'Partner', 'User']
    config_meterType = 25  # Meter type [String] ['Admin', 'Partner', 'User']
    config_meterID = 26  # Meter identification [String] ['Admin', 'Partner', 'User']
    state_OBISListIdentifier = 27  # OBIS List version identifier [String] ['Admin', 'Partner']
    config_gridType = 29  # 0=Unknown, 1=TN, 2=IT, [Integer] ['Admin', 'Partner', 'User']
    config_numPhases = 30  # [Integer] ['Admin', 'Partner', 'User']
    state_currentL1 = 31  # Current in Amps [Double] ['Admin', 'Partner', 'User']
    state_currentL2 = 32  # Current in Amps [Double] ['Admin', 'Partner', 'User']
    state_currentL3 = 33  # Current in Amps [Double] ['Admin', 'Partner', 'User']
    state_voltageNL1 = 34  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_voltageNL2 = 35  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_voltageNL3 = 36  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_voltageL1L2 = 37  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_voltageL1L3 = 38  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_voltageL2L3 = 39  # Voltage in Volts [Double] ['Admin', 'Partner', 'User']
    state_activePowerImport = 40  # Active Power Import in kW [Double] ['Admin', 'Partner', 'User']
    state_activePowerExport = 41  # Active Power Export in kW [Double] ['Admin', 'Partner', 'User']
    state_reactivePowerImport = 42  # Reactive Power Import in kVAR [Double] ['Admin', 'Partner', 'User']
    state_reactivePowerExport = 43  # Reactive Power Export in kVAR [Double] ['Admin', 'Partner', 'User']
    state_maxPowerImport = 44  # Maximum power import[event] [Double] ['Admin', 'Partner', 'User']
    state_cumulativeActivePowerImport = (
        45  # Cumulative Active Power Import in kWh [Double] ['Admin', 'Partner', 'User']
    )
    state_cumulativeActivePowerExport = (
        46  # Cumulative Active Power Export in kWh [Double] ['Admin', 'Partner', 'User']
    )
    state_cumulativeReactivePowerImport = (
        47  # Cumulative Reactive Power Import in kVARh [Double] ['Admin', 'Partner', 'User']
    )
    state_cumulativeReactivePowerExport = (
        48  # Cumulative Reactive Power Export in kVARh [Double] ['Admin', 'Partner', 'User']
    )
    state_clockAndDateMeter = 49  # Clock and Date from Meter [String] ['Admin', 'Partner', 'User']
    state_rcpi = 50  # Received Channel Power Indicator (dBm) [Double] ['Admin', 'Partner', 'User']
    config_ssid = 51  # WIFI SSID  [String] ['Admin', 'Partner', 'User']
    config_masterBackPlateID = 55  # Back Plate RFID of master charger [event] [String] ['Admin', 'Partner', 'User']
    config_equalizerID = 56  # Back Plate RFID of equalizer [boot] [String] ['Admin', 'Partner', 'User']
    config_childReport = 57  # Child configuration in Equalizer [String] ['Admin', 'Partner', 'User']
    state_connectivityReport = 58  # Child connectivity [String] ['Admin', 'Partner']
    state_exceptionData = 60  # Exception Debug Information [boot] [String] ['Admin', 'Partner']
    state_bootReason = 61  # (Re)boot reason [boot] [String] ['Admin', 'Partner']
    state_highCurrentTransitions = (
        64  # Number of transitions to high current mode (Debug) [Integer] ['Admin', 'Partner']
    )
    state_vCap = 65  # Capacitor Voltage in Volts [Double] ['Admin', 'Partner']
    state_vBusMin = 66  # Minimum Bus Voltage in Volts [Double] ['Admin', 'Partner']
    state_vbusMax = 67  # Maximum Bus Voltage in Volts [Double] ['Admin', 'Partner']
    state_internalTemperature = 68  # Internal temperature in Celsius [Double] ['Admin', 'Partner']
    state_meterDataSnapshot = 69  # Meter data snapshot [String] ['Admin', 'Partner']
    state_localRSSI = 70  # Local radio signal strength [dBm][telemetry] [Integer] ['Admin', 'Partner', 'User']
    state_localTxPower = 71  # Local radio transmission power [dBm][telemetry] [Integer] ['Admin', 'Partner']
    state_localRadioChannel = 72  # Local radio channel nr 0 - 11 [telemetry] [Integer] ['Admin', 'Partner']
    state_localShortAddress = (
        73  # Address of equalizer on local radio network [telemetry] [Integer] ['Admin', 'Partner']
    )
    state_localNodeType = 74  # 0-Unconfigured, 1 - Coordinator, 2 - Range extender, 3 - End device, 4- Sleepy end device [telemetry] [Integer] ['Admin', 'Partner']
    state_localParentAddress = 75  # Address of parent on local radio network. If 0 - master, else extender [telemetry] [Integer] ['Admin', 'Partner']
    config_circuitPhaseMapping = 80  # Mapping between EQ phases and charger phases [String] ['Admin', 'Partner']
    state_phaseMappingReport = 81  # Charger vs Meter phase correlation report [String] ['Admin', 'Partner']
    state_phaseLearningStatus = 82  # Status of the phaselearning/loadbalancing [String] ['Admin', 'Partner']
    config_modbusConfiguration = 85  # Complete Modbus Configuration [String] ['Admin', 'Partner', 'User']
    state_loadbalanceThrottle = 86  # Throttle level [percent] [Integer] ['Admin', 'Partner']
    state_availableCurrentL1 = 87  # Available Current for Balancing in Amps [Double] ['Admin', 'Partner', 'User']
    state_availableCurrentL2 = 88  # Available Current for Balancing in Amps [Double] ['Admin', 'Partner', 'User']
    state_availableCurrentL3 = 89  # Available Current for Balancing in Amps [Double] ['Admin', 'Partner', 'User']
    state_meterErrors = 90  # Meter Errors [Integer] ['Admin', 'Partner']
    state_APMacAddress = 91  # Mac Address of the Wifi access point [String] ['Admin', 'Partner']
    state_wifiReconnects = 92  # Number of sucessful reconnects to AP [Integer] ['Admin', 'Partner']
    state_ledMode = 100  # Current LED pattern [Integer] ['Admin', 'Partner', 'User']
    state_equalizedChargeCurrentL1 = (
        105  # Charge current controlled by Equalizer in Amps [Double] ['Admin', 'Partner', 'User']
    )
    state_equalizedChargeCurrentL2 = (
        106  # Charge current controlled by Equalizer in Amps [Double] ['Admin', 'Partner', 'User']
    )
    state_equalizedChargeCurrentL3 = (
        107  # Charge current controlled by Equalizer in Amps [Double] ['Admin', 'Partner', 'User']
    )
    config_currentTransformerConfig = 110  # Current Transformer Configuration [String] ['Admin', 'Partner', 'User']
    state_meterEncryptionStatus = 111  # Meter Encryption Status [String] ['Admin', 'Partner', 'User']
    config_surplusCharging = 115  # Surplus charging configuration [String] ['Admin', 'Partner', 'User']
    state_connectedAmps = 120  # Equalizer AMPs report ['Admin', 'Partner', 'User']
    state_connectedToCloud = 250  # Device is connected to AWS [Boolean] ['Admin', 'Partner', 'User']
    state_cloudDisconnectReason = 251  # AWS DisconnectReason [String] ['Admin', 'Partner', 'User']


# Data IDs for Equalizer from signalr stream
class DatatypesStreamData(Enum):
    Binary = 1
    Boolean = 2
    Double = 3
    Integer = 4
    Position = 5
    String = 6
    Statistics = 7
