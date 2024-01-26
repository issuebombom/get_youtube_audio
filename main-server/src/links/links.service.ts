import { HttpService } from '@nestjs/axios';
import { HttpException, Injectable } from '@nestjs/common';
import { InjectModel } from '@nestjs/mongoose';
import { lastValueFrom } from 'rxjs';
import { Link } from './schemas/links.schema';
import { Model } from 'mongoose';

@Injectable()
export class LinksService {
  constructor(
    private httpService: HttpService,
    @InjectModel(Link.name) private linkModel: Model<Link>,
  ) {}

  async createLinksInformation({ sendLinksMessageDto }) {
    try {
      const res = await lastValueFrom(
        this.httpService.post(
          'http://127.0.0.1:5000/links',
          sendLinksMessageDto,
        ),
      );
      const result = await this.linkModel.insertMany(res.data);
      return result;
    } catch (err) {
      return err.response.data ?? err;
    }
  }
}
