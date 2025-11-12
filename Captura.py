from saleae import automation
import os
import os.path
import time


def capturaDatos():
    
    #Connect to the running Logic 2 Application on port `10430`.
    #Alternatively you can use automation.Manager.launch() to launch a new Logic 2 process - see
    #the API documentation for more details.
    #Using the `with` statement will automatically call manager.close() when exiting the scope. If you
    #want to use `automation.Manager` outside of a `with` block, you will need to call `manager.close()` manually.

    with automation.Manager.connect(port=10430) as manager:

        # Configure the capturing device to record on digital channels 0, 1, 2, and 3,
        # with a sampling rate of 10 MSa/s, and a logic level of 3.3V.
        # The settings chosen here will depend on your device's capabilities and what
        # you can configure in the Logic 2 UI.
        device_configuration = automation.LogicDeviceConfiguration(
            enabled_digital_channels=[0],
            digital_sample_rate=50_000_000,
            digital_threshold_volts=3.3
        )

        # Record 5 seconds of data before stopping the capture
        # capture_configuration = automation.CaptureConfiguration(
        # capture_mode=automation.DigitalTriggerCaptureMode(trigger_type=automation.DigitalTriggerType.PULSE_LOW,
        #                                                     min_pulse_width_seconds=0.0119,
        #                                                     max_pulse_width_seconds=0.0132,
        #                                                     trigger_channel_index=1, 
        #                                                     trim_data_seconds=0, 
        #                                                     after_trigger_seconds=4.5,
        #                                                     linked_channels=[automation.DigitalTriggerLinkedChannel(channel_index=2,state=automation.DigitalTriggerLinkedChannelState.LOW)])
        # )

        capture_configuration = automation.CaptureConfiguration(
            capture_mode=automation.TimedCaptureMode(duration_seconds=4.5)
        )

        # Start a capture - the capture will be automatically closed when leaving the `with` block
        # Note: The serial number 'F4241' is for the Logic Pro 16 demo device.
        #       To use a real device, you can:
        #         1. Omit the `device_id` argument. Logic 2 will choose the first real (non-simulated) device.
        #         2. Use the serial number for your device. See the "Finding the Serial Number
        #            of a Device" section for information on finding your device's serial number.


        with manager.start_capture(
                device_id='70F8D553C013FA25',
                device_configuration=device_configuration,
                capture_configuration=capture_configuration) as capture:

            # Wait until the capture has finished
            # This will take about 5 seconds because we are using a timed capture mode
            print('Iniciando captura')
            capture.wait()


            man_analysis = capture.add_analyzer('Manchester', label='arruspuchuchu',settings={
                'Manchester': 0,
                'Mode': 'Manchester',
                'Bit Rate (Bits/s)': 1000000,
                'Edge Polarity': 'negative edge is binary one',
                'Bits Per Frame': '1 Bit per Transfer',
                'Significant Bit': 'Least Significant Bit Sent First',
                'Preamble bits to ignore': 0})
            # Store output in a timestamped directory
            output_dir = os.path.join(os.getcwd(), 'output')
            os.makedirs(output_dir,exist_ok=True)

            # Export raw digital data to a CSV file
            capture.legacy_export_analyzer(filepath=output_dir+'\salida.csv',analyzer=man_analysis,radix=automation.RadixType.DECIMAL)

            print('archivo guardado')

if __name__=="__main__":
    capturaDatos()