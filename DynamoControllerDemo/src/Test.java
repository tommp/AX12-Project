import jgamepad.Controller;
import jgamepad.enums.Analog;
import objects.Action;
import objects.Actuator;

public class Test {

    public static void main(String[] args){

//        objects.Car car = new objects.Car(1, 2, 3, 4);
//        String json = JSONConverter.toJson(car);
//        objects.Car responseCar = (objects.Car) JSONConverter.fromJson(json, objects.Car.class);
//        System.out.println(responseCar);

//        Actuator actuator1 = new Actuator(2, 50);
//        Actuator actuator2 = new Actuator(4, 20);
//
//        Action action = new Action("move", new Actuator[] {actuator1, actuator2});
//
//        System.out.println(JSONConverter.toJson(action));


        Controller.dllPath = System.getProperty("user.dir") + "\\libs";
        Controller controller = new Controller(0, 50);

        while (true){
            System.out.println(controller.getAnalogValue(Analog.R2));
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}
