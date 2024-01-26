import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { LinksModule } from './links/links.module';
import { MongooseModule } from '@nestjs/mongoose';
import { ConfigModule } from '@nestjs/config';

@Module({
  imports: [
    ConfigModule.forRoot({ envFilePath: '../.env.development', isGlobal: true }),
    MongooseModule.forRoot(
      `mongodb+srv://${process.env.MONGO_ID}:${process.env.MONGO_PW}@${process.env.MONGO_CLUSTER}.udxtbwr.mongodb.net/?retryWrites=true&w=majority`,
    ),
    LinksModule,
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
