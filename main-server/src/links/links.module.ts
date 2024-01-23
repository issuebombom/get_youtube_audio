import { Module } from '@nestjs/common';
import { LinksController } from './links.controller';
import { HttpModule } from '@nestjs/axios';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { LinksKafkaProducerService } from './links.kafka-producer.service';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: 'YOUTUBE_SERVICE',
        transport: Transport.KAFKA,
        options: {
          client: {
            clientId: 'test-client-1',
            brokers: ['kafka:19092'],
          },
          consumer: {
            groupId: 'test-group-1',
          },
        },
      },
    ]),
    HttpModule.register({
      timeout: 30000,
      maxRedirects: 5,
    }),
  ],
  controllers: [LinksController],
  providers: [LinksKafkaProducerService],
})
export class LinksModule {}
