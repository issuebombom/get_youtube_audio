import { Kafka, logLevel } from 'kafkajs';

const kafka = new Kafka({
  clientId: 'test-client-1',
  brokers: ['kafka:19092'],
  logLevel: logLevel.ERROR,
});
export const kafkaProducer = kafka.producer();
export const kafkaConsumer = kafka.consumer({ groupId: 'test-group-1' });
