import { Module } from '@nestjs/common';
import { LinksController } from './links.controller';
import { ClientsModule, Transport } from '@nestjs/microservices';
import { LinksKafkaProducerService } from './links.kafka-producer.service';
import { MongooseModule } from '@nestjs/mongoose';
import { Link, LinkSchema } from './schemas/links.schema';
import { HttpModule } from '@nestjs/axios';
import { LinksService } from './links.service';

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
    MongooseModule.forFeature([
      {
        name: Link.name,
        schema: LinkSchema,
        collection: 'youtube',
      },
    ]),
    HttpModule.register({
      timeout: 30000,
      maxRedirects: 5,
    }),
  ],
  controllers: [LinksController],
  providers: [LinksKafkaProducerService, LinksService],
})
export class LinksModule {}
