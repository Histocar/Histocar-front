CREATE TABLE IF NOT EXISTS "histocar_matricula" (
	"id" serial PRIMARY KEY NOT NULL,
	"matricula" varchar(255) NOT NULL,
	"data" jsonb NOT NULL,
	"created_by" varchar(255) NOT NULL,
	"created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
	"updated_at" timestamp with time zone
);
--> statement-breakpoint
DO $$ BEGIN
 ALTER TABLE "histocar_matricula" ADD CONSTRAINT "histocar_matricula_created_by_histocar_user_id_fk" FOREIGN KEY ("created_by") REFERENCES "public"."histocar_user"("id") ON DELETE no action ON UPDATE no action;
EXCEPTION
 WHEN duplicate_object THEN null;
END $$;
--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "matricula_idx" ON "histocar_matricula" USING btree ("matricula");--> statement-breakpoint
CREATE INDEX IF NOT EXISTS "matricula_created_by_idx" ON "histocar_matricula" USING btree ("created_by");