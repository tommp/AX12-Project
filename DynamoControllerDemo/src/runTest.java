import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class runTest {

    public static String URL = "http://vsop.online.ntnu.no:8080";

    public static void main(String[] args){
        try {
            sendPost();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private static void sendPost() throws Exception {

        String USER_AGENT = "Mozilla/5.0";

        URL obj = new URL(URL);
        HttpURLConnection con = (HttpURLConnection) obj.openConnection();

        //add reuqest header
        con.setRequestMethod("POST");
        con.setRequestProperty("User-Agent", USER_AGENT);
        con.setRequestProperty("Accept-Language", "en-US,en;q=0.5");
        con.setRequestProperty("Content-Type", "application/json");

        String urlParameters = "{ \"action\": \"move\"," +
                "\"actuators\": [" +
                "{\"id\":4, \"direction\":" + "\"clockwise\"" + ", \"speed\":" + 50 + "}," +
                "{\"id\":2, \"direction\":" + "\"clockwise\"" + ", \"speed\":" + 20 + "}" +
                "]}";

//        String urlParameters = "{ \"action\": \"info\"," +
//                "\"objects\": [" +
//                "{\"id\":4}," +
//                "{\"id\":2}" +
//                "]}";

        // Send post request
        con.setDoOutput(true);
        DataOutputStream wr = new DataOutputStream(con.getOutputStream());
        wr.writeBytes(urlParameters);
        wr.flush();
        wr.close();

        int responseCode = con.getResponseCode();
        System.out.println("\nSending 'POST' request to URL : " + URL);
        System.out.println("Post parameters : " + urlParameters);
        System.out.println("Response Code : " + responseCode);

        BufferedReader in = new BufferedReader(
                new InputStreamReader(con.getInputStream()));
        String inputLine;
        StringBuffer response = new StringBuffer();

        while ((inputLine = in.readLine()) != null) {
            response.append(inputLine);
        }
        in.close();

        //print result
        System.out.println(response.toString());

    }
}
