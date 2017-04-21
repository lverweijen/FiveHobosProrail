import java.io.*;
import org.json.simple.*;
import org.json.simple.parser.*;

public class DummyRegionMatcher
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
		System.err.println("dummy region matcher java is done!");
	}
	
	@SuppressWarnings("unchecked")
	static void process(JSONObject data)
	{
		int frameNr = ((Number)data.get("frameNr")).intValue();
		int width = ((Number)data.get("width")).intValue();
		float offset = frameNr * 0.2f * width;

		JSONObject outData = new JSONObject();
		outData.put("leftEdge", (int)offset);
		outData.put("frameNr", frameNr);
		outData.put("xtra", width);
		System.out.println(outData);
	}
}