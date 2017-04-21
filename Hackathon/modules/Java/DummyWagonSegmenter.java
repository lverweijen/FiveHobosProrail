import java.io.*;
import org.json.simple.*;
import org.json.simple.parser.*;

public class DummyWagonSegmenter
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
		System.err.println("dummy wagon segmenter java is done!");
	}

	static int wagonStart;
	
	@SuppressWarnings("unchecked")
	static void process(JSONObject data)
	{
		int leftEdge = ((Number)data.get("leftEdge")).intValue();
		if (Math.abs(leftEdge - wagonStart) > 3300)
		{
			int wagonEnd = wagonStart + 3300;
			JSONObject outData = new JSONObject();
			outData.put("wagonStart", wagonStart);
			outData.put("wagonEnd", wagonEnd);
			outData.put("xtradata", leftEdge);
			System.out.println(outData);

			wagonStart = wagonEnd;
		}
	}
}