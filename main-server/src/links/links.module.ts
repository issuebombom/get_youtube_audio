import { Module } from '@nestjs/common';
import { LinksController } from './links.controller';
import { LinksKafkaService } from './links.kafka.service';
import { kafkaConsumer, kafkaProducer } from './links.kafka.config';

@Module({
  imports: [],
  controllers: [LinksController],
  providers: [
    {
      provide: 'KafkaProducer',
      useValue: kafkaProducer,
    },
    {
      provide: 'KafkaConsumer',
      useValue: kafkaConsumer,
    },
    LinksKafkaService,
  ],
})
export class LinksModule {}
