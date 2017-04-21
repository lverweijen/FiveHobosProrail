import java.io.*;
import java.util.*;
import org.json.simple.*;
import org.json.simple.parser.*;

public class DummyNumberRecogniser
{
	public static void main(String[] args) throws IOException
	{
		try (BufferedReader br = new BufferedReader(new InputStreamReader(System.in)))
		{
			String line;
			while ((line = br.readLine()) != null)
			{
				Object obj = JSONValue.parse(line);
				if (obj instanceof JSONObject)
				{
					process((JSONObject)obj);
				}
			}
		}
		System.err.println("dummy number recogniser java is done!");
	}
	
	@SuppressWarnings("unchecked")
	static void process(JSONObject data)
	{
		int frameSum = 0;
		List numberLocations = (List)data.get("numberLocations");
		for (Object numberLocation : numberLocations)
		{
			int frameNr = ((Number)((Map)numberLocation).get("frameNr")).intValue();
			frameSum += frameNr;
		}
		float averageFrame = frameSum / (float)numberLocations.size();
		int digits = (int)(averageFrame * 218); // Just some random multiplication to get more digits
		int checksum = generateUICChecksum(digits);
		String uic = String.format("%011d-%d", digits, checksum);

		JSONObject outData = new JSONObject();
		outData.put("wagonStart", data.get("wagonStart"));
		outData.put("number", uic);

		System.out.println(outData);
	}

	static int generateUICChecksum(long digits)
	{
		boolean evenPosition = false;
		int sum = 0;
		while (digits > 0)
		{
			int factor = evenPosition ? 1 : 2;
			int digit = (digits % 10) * factor;
			while (digit > 0)
			{
				sum += digit % 10;
				digit /= 10;
			}
			digits /= 10;
			evenPosition = !evenPosition;
		}
		int roundUp = 10 * (int)Math.ceil(sum / 10.0f);
		return roundUp - sum;
	}
}