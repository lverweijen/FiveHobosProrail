import java.awt.Polygon;
import java.awt.geom.*;
import java.io.*;
import java.util.*;
import org.json.simple.*;
import org.json.simple.parser.*;

public class DummyNumberLocaliser
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
		System.err.println("dummy number localiser java is done!");
	}

	static Point2D[] prototype = new Point2D[]
	{
		new Point2D.Float(0.1f, 0.3f),
		new Point2D.Float(0.2f, 0.3f),
		new Point2D.Float(0.2f, 0.4f),
		new Point2D.Float(0.5f, 0.4f),
		new Point2D.Float(0.5f, 0.5f),
		new Point2D.Float(0.1f, 0.5f)
	};
	
	@SuppressWarnings("unchecked")
	static void process(JSONObject data)
	{
		// Gather some information about this wagon and the images
		int wagonStart = ((Number)data.get("wagonStart")).intValue();
		int wagonEnd = ((Number)data.get("wagonEnd")).intValue();
		int wagonWidth = wagonEnd - wagonStart;
		List frames = (List)data.get("frames");
		Map frame0 = (Map)frames.get(0);
		int frameHeight = ((Number)frame0.get("height")).intValue();
		int frameWidth = ((Number)frame0.get("width")).intValue();

		JSONArray numberLocations = new JSONArray();
		// Allocate some space for a single polygon. If you output multiple polygons
		// you must allocate new arrays for each of them.
		int[] x = new int[prototype.length];
		int[] y = new int[prototype.length];
		for (Object frame : frames)
		{
			// Construct a polygon for the current frame
			int leftEdge = ((Number)((Map)frame).get("leftEdge")).intValue();
			fillPolygonPoints(x, y, wagonStart - leftEdge, wagonWidth, frameHeight);
			if (new Polygon(x, y, prototype.length).intersects(0, 0, frameWidth, frameHeight))
			{
				// Only add the localised polygon if it actually appears in this frame
				JSONArray points = new JSONArray();
				for (int index = 0; index < prototype.length; index++)
				{
					JSONArray point = new JSONArray();
					point.add(x[index]);
					point.add(y[index]);
					points.add(point);
				}
				JSONObject polygon = new JSONObject();
				polygon.put("points", points);
				polygon.put("score", 0.95);
				// Wrap our single polygon in the array of polygons. Add more polygons to this if you like
				JSONArray polygons = new JSONArray();
				polygons.add(polygon);
				// And put the polygons array in the locations object
				JSONObject locations = new JSONObject();
				locations.put("frameNr", ((Map)frame).get("frameNr"));
				locations.put("polygons", polygons);
				numberLocations.add(locations);
			}
		}

		JSONObject outData = new JSONObject();
		outData.put("wagonStart", wagonStart);
		outData.put("numberLocations", numberLocations);
		System.out.println(outData);
	}

	/**
	 * Translate a prototype polygon to local coordinates. The prototype is a static member of this class
	 * and is defined in normalised coordinates. The output is translated to image coordinates and written
	 * to the provided x and y arrays.
	 * @param x Output array that will contain the local x coordinates
	 * @param y Output array that will contain the local y coordinates
	 * @param start Offset in the x direction
	 * @param width 
	 * @param height
	 */
	static void fillPolygonPoints(int[] x, int[] y, int start, int width, int height)
	{
		for (int index = 0; index < prototype.length; index++)
		{
			Point2D p = prototype[index];
			x[index] = (int)(start + p.getX() * width);
			y[index] = (int)(p.getY() * height);
		}
	}
}