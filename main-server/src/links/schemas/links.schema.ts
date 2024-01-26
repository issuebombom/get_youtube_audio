import { Prop, Schema, SchemaFactory } from '@nestjs/mongoose';
import { HydratedDocument } from 'mongoose';

export type LinkDocument = HydratedDocument<Link>;

@Schema()
export class Link {
  @Prop({ required: true })
  title: string;

  @Prop()
  thumbnail_url: string;

  @Prop()
  channel_id: string;

  @Prop()
  length: string;

  @Prop({ required: true })
  url: string;
}

export const LinkSchema = SchemaFactory.createForClass(Link);
