import scala.collection.mutable.ArrayBuffer
import org.apache.spark.SparkConf
import org.apache.spark.streaming.{Seconds, StreamingContext}
import org.apache.spark.SparkContext
import org.elasticsearch.spark.rdd.EsSpark                        
import org.elasticsearch.spark._
import org.apache.spark.sql._
import org.elasticsearch.spark.sql._
import java.nio.ByteBuffer
import java.lang.Float
/**
 * Counts bytes in binary files created in the given directory
 * Usage: HdfsByteCount &lt;directory&gt;
 *   &lt;directory&gt; is the directory that Spark Streaming will use to find and read new binary files.
 *
 * To run this on your local machine on directory `localdir`, run this example
 *    $ bin/run-example \
 *       org.hdfgroup.spark.HdfsByteCount localdir
 *
 * Then create a binary file in `localdir` and the number of the bytes will
 * get counted. The value in the binary file will be indexed by Elastic Search.
 */
object HdfsByteCount {
  def b2s(a: Array[Byte]): String = {
      println(a.deep.mkString("\n"))
      val f = ByteBuffer.wrap(a).getFloat
      val s = Float.toString(f)
      val str = "{\"name\":\""+s+"\", \"location\": \"40.715, -74.011\"}"
      println(str)
      return str      
  }
       
  def main(args: Array[String]) {
    if (args.length &lt; 1) {
      System.err.println("Usage: HdfsByteCount &lt;directory&gt;")
      System.exit(1)
    }


    val sparkConf = new SparkConf().setAppName("HdfsByteCount")
    sparkConf.set("es.nodes", "giraffe")

    // Create the context. Check every 2 second.
    val ssc = new StreamingContext(sparkConf, Seconds(2))

    // Create the FileInputDStream on the directory and use the
    // stream to count bytes in new files created
    val bytes = ssc.binaryRecordsStream(args(0), 4)
    // val arr = new ArrayBuffer[String]
    bytes.foreachRDD(rdd =&gt; {
        if(!rdd.partitions.isEmpty) {
            val sc = rdd.context
            val sqlContext = new SQLContext(sc)
            val rdd2 = rdd.map(r=&gt;b2s(r))
            val log = sqlContext.jsonRDD(rdd2)
            log.saveToEs("attractions/restaurant")
        }
    })
    val count = bytes.count()
    count.print()
    ssc.start()
    ssc.awaitTermination()
  }
}

