import { Module } from '@nestjs/common';
import { LinksController } from './links.controller';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { LinksKafkaProducerService } from './links.kafka-producer.service';

@Module({
  imports: [
    ClientsModule.register([
      {
        name: 'LINK_SERVICE',
        transport: Transport.KAFKA,
        options: {
          client: {
            clientId: 'main-links-1',
            brokers: ['kafka-1:19092'],
          },
        },
      },
    ]),
  ],
  controllers: [LinksController],
  providers: [LinksKafkaProducerService],
})
export class LinksModule {}
