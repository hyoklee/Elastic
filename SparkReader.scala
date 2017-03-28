import org.apache.spark.SparkConf
import org.apache.spark.SparkContext
import org.elasticsearch.spark.rdd.EsSpark
import org.elasticsearch.spark._


val sparkConf = new SparkConf().setAppName("ElasticSearch")
sparkConf.set("es.nodes", "10.10.10.154")
// sparkConf.set("es.nodes.wan.only","true")
// parkConf.set("es.nodes.client.only","true")
val sc = new SparkContext(sparkConf)
val RDDs = sc.esRDD("merra2-monthly/float32", "?q=PRECCU AND chunk_position:\\[0,91,288\\] AND filename:MERRA2_100*", Map[String, String]("es.read.field.include"->"filename,md5"))
// Quick check
System.out.println(RDDs.take(1))
RDDs.count()
// This works for master.
// RDDs.collect().foreach(println)
RDDs.foreach(map())
val vectors = RDDs.map(x => x._2.map(y => y._2))
val dropleft = vectors.map(x => x.drop(1))
val md5s = dropleft.map(x => x.mkString)
import play.api.libs.ws.ning.NingWSClient
