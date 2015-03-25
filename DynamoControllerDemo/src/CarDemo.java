import jgamepad.Controller;
import jgamepad.enums.Analog;
import jgamepad.enums.Button;
import jgamepad.interfaces.ButtonPressedEvent;
import jgamepad.listeners.ButtonPressedListener;
import objects.Action;
import objects.Car;
import objects.Response;

public class CarDemo {

    private static final String URL = "http://78.91.51.239:9002";
    //private static final String URL = "http://vsop.online.ntnu.no:9002";
    private static final String DEVICE_NAME = "ruls";

    private static int RIGHT_ANALOG_MAX_VALUE = 24078;
    private static int LEFT_ANALOG_MAX_VALUE = 24918;
    private static int ANALOG_TRIGGER_MAX = 255;

    private static int lastRightAnalogValue;
    private static int lastRightTriggerValue;
    private static int lastLeftTriggerValue;
    private static int carId = 0;

    public static void main(String[] args){
        Connection connection = new Connection(URL, DEVICE_NAME);
        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0, 50);

        //String responseString = connection.sendPostMessage(createCarMessage(1,2,3,4));
        String responseString = connection.sendPostMessage(createCarMessage(2,4, 0, 0));

        Response response = (Response) JSONConverter.fromJson(responseString, Response.class);

        if(response.getStatus().equals("success"))
            carId = Integer.parseInt(response.getMessage());

        controller.addButtonListener(new ButtonPressedListener(Button.A, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveCarMessage(0, 0);
                    connection.sendPostMessage(message);
                }
            }
        }));

        controller.addButtonListener(new ButtonPressedListener(Button.B, new ButtonPressedEvent() {
            @Override
            public void run(boolean pressed) {
                if(pressed){
                    System.out.println("Turning off");
                    String message = generateMoveCarMessage(50, 0);
                    connection.sendPostMessage(message);
                }
            }
        }));


        runWithTrigger(controller, connection);


    }

    private static int getPercentage(int analogValue, int max){
        double speed = (double) analogValue / max * 100;
        return (int) speed;
    }

    private static String generateMoveCarMessage(int speed, int direction){

        Action action = new Action("moveDevice", carId, speed, direction);

        return JSONConverter.toJson(action);
    }

    private static String createCarMessage(int topLeft, int topRight, int bottomLeft, int bottomRight){
        Car car = new Car(topLeft, topRight, bottomLeft, bottomRight);

        return JSONConverter.toJson(car);
    }

    private static void runWithAnalogStick(Controller controller, Connection connection){
        while(true){
            try {
                int rightAnalogValue = controller.getAnalogValue(Analog.rightStickY);
                if(rightAnalogValue != 0 || lastRightAnalogValue != 0) {
                    lastRightAnalogValue = rightAnalogValue;
                    int speed = getPercentage(rightAnalogValue, RIGHT_ANALOG_MAX_VALUE);
                    int direction = getPercentage(controller.getAnalogValue(Analog.leftStickX), LEFT_ANALOG_MAX_VALUE);

                    String message = generateMoveCarMessage(speed, direction);
                    connection.sendPostMessage(message);
                }
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }

    private static void runWithTrigger(Controller controller, Connection connection){
        while(true){
            try {
                int rightTriggerValue = controller.getAnalogValue(Analog.R2);
                int leftTriggerValue = controller.getAnalogValue(Analog.L2);
                if(rightTriggerValue != 0 || lastRightTriggerValue != 0) {
                    lastRightTriggerValue = rightTriggerValue;
                    int speed = getPercentage(rightTriggerValue, ANALOG_TRIGGER_MAX);
                    int direction = getPercentage(controller.getAnalogValue(Analog.rightStickX), RIGHT_ANALOG_MAX_VALUE);

                    String message = generateMoveCarMessage(speed, direction);
                    connection.sendPostMessage(message);
                }
                else if(leftTriggerValue != 0 || lastLeftTriggerValue != 0) {
                    lastLeftTriggerValue = leftTriggerValue;
                    int speed = getPercentage(leftTriggerValue * -1, ANALOG_TRIGGER_MAX);
                    int direction = getPercentage(controller.getAnalogValue(Analog.rightStickX), RIGHT_ANALOG_MAX_VALUE);

                    String message = generateMoveCarMessage(speed, direction);
                    connection.sendPostMessage(message);
                }
                Thread.sleep(50);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
