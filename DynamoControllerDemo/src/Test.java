import jgamepad.Controller;
import jgamepad.enums.Analog;

public class Test {

    public static void main(String[] args){

//        Car car = new Car(1, 2, 3, 4);
//        String json = JSONConverter.toJson(car);
//        Car responseCar = (Car) JSONConverter.fromJson(json, Car.class);
//        System.out.println(responseCar);

        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0);

        while (true){
            System.out.println(controller.getAnalogValue(Analog.leftStickX));
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
