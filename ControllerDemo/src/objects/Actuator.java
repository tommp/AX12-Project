package objects;

public class Actuator {

    private int id;
    private int speed;
    private int angle;
    private int clockwise;
    private int counterclockwise;

    public Actuator(int id, int speed) {
        this.id = id;
        this.speed = speed;
    }
//
//    public Actuator(int id, int speed, int angle) {
//        this.id = id;
//        this.angle = angle;
//    }

    public Actuator(int id, int clockwise, int counterclockwise) {
        this.id = id;
        this.angle = angle;
    }
}
