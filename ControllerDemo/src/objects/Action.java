package objects;

public class Action {

    private String action;
    private Actuator[] actuators;
    private int id;
    private int speed;
    private int direction;

    public Action(String action, Actuator[] actuators) {
        this.action = action;
        this.actuators = actuators;
    }

    public Action(String action, int id, int speed, int direction) {
        this.action = action;
        this.id = id;
        this.speed = speed;
        this.direction = direction;
    }
}
